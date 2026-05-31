"""
MN2MC Python Backend - TCP server bridging mn2mc_proxy with aiorak event handlers.

Architecture:
    [MiniWorld Client] --UDP--> [mn2mc_proxy.exe] --TCP:19134--> [this backend]

The C++ proxy handles RakNet + NAT punchthrough. This backend handles all game
protocol logic (enter world, chat, move, etc.) via the existing aiorak event handlers.

Bridge protocol (per frame):
    [4B frame_len LE] [4B client_guid LE] [data]
    frame_len = 4 + len(data)

Control frames (from C++ proxy):
    data = [0x00, 0x01]  -> client connected
    data = [0x00, 0x02]  -> client disconnected
Game frames:
    data starts with 0x89 (raw C2S packet)
"""
import asyncio
import json
import struct
import sys
import time
import zlib

import aiorak
from loguru import logger

import mn2mc
import mn2mc.config as config
import mn2mc.mini.auth
import mn2mc.mini.proto as proto
import mn2mc.mini.room
import mn2mc.mini.wsconn
import mn2mc.utils.protobuf_parser as protobuf_parser
from mn2mc.mini.packet import (
    MiniClientPacket,
    on_event,
    load_all_event as mini_load_all_event,
)
from mn2mc.mini.player import MiniPlayer, players


class FakeConnection:
    """Mock aiorak.Connection that pipes sends through the TCP bridge."""

    def __init__(self, guid: int, backend: "BackendServer"):
        self.remote_guid = guid
        self.remote_address = (f"client_{guid}", 0)
        self.state = aiorak.ConnectionState.CONNECTED
        self._backend = backend

    def send(self, data: bytes, reliability=None, priority=None):
        if self.state != aiorak.ConnectionState.CONNECTED:
            return
        self._backend.send_to_client(self.remote_guid, data)

    def disconnect(self):
        self.state = aiorak.ConnectionState.DISCONNECTED


# ============================================================
# Initial packet builders (extracted from mn2mc.mini.server.handler)
# ============================================================

def _varint(value):
    buf = b""
    while value > 0x7F:
        buf += bytes([(value & 0x7F) | 0x80])
        value >>= 7
    buf += bytes([value & 0x7F])
    return buf


def _tag(field, wire_type=2):
    return _varint((field << 3) | wire_type)


def _field_bytes(field, data):
    return _tag(field, 2) + _varint(len(data)) + data


def _field_varint(field, val):
    return _tag(field, 0) + _varint(val)


def _field_sint32(field, val):
    zigzag = (val << 1) ^ (val >> 31)
    return _tag(field, 0) + _varint(zigzag & 0xFFFFFFFF)


# ============================================================
# PB_BlockUpdateHC (cmd 104) - 服务端方块更新包
# 位编码 (逆向自客户端 hook):
#   Blocks[i] uint32 = (block_pack << 16) | pos16
#     pos16 = (z << 12) | (y << 4) | x   // z/x: 4 bits, y: 8 bits
#     block_pack = (state << 12) | (block_id & 0xFFF)
#   BlocksEx[i] = block_id 高位 (id >= 4096 时用)
#   BlockStateIndex[i] = 复杂 state 索引 (一般 0)
# ============================================================

def build_block_update_packet(chunk_x: int, chunk_z: int,
                              changes: list,
                              map_id: int = 0) -> bytes:
    """构造 PB_BlockUpdateHC wire bytes.
    changes: list of (local_x, local_y, local_z, block_id, state) tuples
             local x/z: 0-15, local y: 0-255, block_id: 任意正整数, state: 0-15
    """
    blocks_bytes = b""
    blocks_ex_bytes = b""
    bsi_bytes = b""
    for (lx, ly, lz, bid, state) in changes:
        pos16 = ((lz & 0xF) << 12) | ((ly & 0xFF) << 4) | (lx & 0xF)
        block_pack = ((state & 0xF) << 12) | (bid & 0xFFF)
        packed = (block_pack << 16) | pos16
        blocks_bytes += _field_varint(4, packed)
        # BlocksEx 给 block_id 的高位 (id >> 12)
        blocks_ex_bytes += _field_varint(6, bid >> 12)
        # BlockStateIndex 一般 0
        bsi_bytes += _field_varint(8, 0)

    pkt = (
        _field_sint32(1, chunk_x)
        + _field_sint32(2, chunk_z)
        + _field_varint(3, map_id)
        + blocks_bytes
        + blocks_ex_bytes
        + bsi_bytes
    )
    # DEBUG: log full wire bytes for comparison with real game packets
    from loguru import logger
    logger.debug(
        f"[BUILD-BU] cx={chunk_x} cz={chunk_z} map={map_id} changes={changes} "
        f"wire={pkt.hex()}"
    )
    return pkt


def block_global_to_chunk(gx: int, gy: int, gz: int):
    """全局方块坐标 → (chunk_x, chunk_z, local_x, local_y, local_z)"""
    cx, lx = divmod(gx, 16)
    cz, lz = divmod(gz, 16)
    return cx, cz, lx, gy, lz



# ============================================================
# Real chunk loading from cachetrunk (LZMA1-alone format)
# 文件名: w<OWID>_<MapID>_<cx>_<cz>_<md5>
# 内容: [5B LZMA props][LZMA1 raw stream] -> FlatBuffers binary
# ============================================================

# 用一个固定真实世界的区块缓存作为模板
WORLD_OWID = 72954558563850
WORLD_MAP_ID = 0
CHUNK_CACHE_ROOT = r"C:\Users\PC\AppData\Roaming\miniworddata110\data\cachetrunk"

# 加载到内存的 {(cx, cz): (raw_blob_bytes, unzip_len)}
_real_chunks: "dict[tuple[int, int], tuple[bytes, int]]" = {}


# _real_chunks 现在存 (raw_blob, unzip_len, algo)
# algo: 2=LZMA, 3=ZSTD

def _load_real_chunks() -> int:
    """扫描 cachetrunk 目录,加载 w<WORLD_OWID>_0_* 的真实 chunk.
    支持 LZMA (0x5D) 和 ZSTD (0x28 B5 2F FD) 两种压缩。"""
    import os
    import lzma
    import re
    try:
        import zstandard
    except ImportError:
        zstandard = None

    if not os.path.isdir(CHUNK_CACHE_ROOT):
        return 0

    pattern = re.compile(rf"^w{WORLD_OWID}_{WORLD_MAP_ID}_(-?\d+)_(-?\d+)_")
    count_lzma = 0
    count_zstd = 0
    matched_files = 0
    fail = 0
    fail_unknown = 0

    zstd_dctx = zstandard.ZstdDecompressor() if zstandard else None

    for sub in os.listdir(CHUNK_CACHE_ROOT):
        sub_dir = os.path.join(CHUNK_CACHE_ROOT, sub)
        if not os.path.isdir(sub_dir):
            continue
        for fname in os.listdir(sub_dir):
            if fname.endswith(".decompressed"):
                continue
            m = pattern.match(fname)
            if not m:
                continue
            matched_files += 1
            cx, cz = int(m.group(1)), int(m.group(2))
            path = os.path.join(sub_dir, fname)
            try:
                with open(path, "rb") as f:
                    raw = f.read()
                if len(raw) >= 4 and raw[:4] == b"\x28\xb5\x2f\xfd":
                    # ZSTD
                    if zstd_dctx is None:
                        fail_unknown += 1
                        continue
                    decompressed = zstd_dctx.decompress(raw)
                    _real_chunks[(cx, cz)] = (raw, len(decompressed), 3)
                    count_zstd += 1
                elif len(raw) >= 5 and raw[0] == 0x5D:
                    # LZMA-alone
                    header = raw[:5] + b"\xff" * 8
                    decompressed = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(
                        header + raw[5:]
                    )
                    _real_chunks[(cx, cz)] = (raw, len(decompressed), 2)
                    count_lzma += 1
                else:
                    fail_unknown += 1
                    if fail_unknown <= 3:
                        logger.warning(f"chunk ({cx},{cz}) unknown magic: {raw[:4].hex()}")
            except Exception as e:
                fail += 1
                if fail <= 3:
                    logger.warning(f"chunk ({cx},{cz}) decompress error: {e}")
    total = count_lzma + count_zstd
    logger.info(f"chunk scan: matched={matched_files}, loaded={total} (zstd={count_zstd}, lzma={count_lzma}), fail={fail}, unknown={fail_unknown}")
    return total


def _build_chunk_packet_real(cx: int, cz: int) -> bytes | None:
    """用真实压缩 cache 文件构造 chunk 包."""
    entry = _real_chunks.get((cx, cz))
    if entry is None:
        return None
    raw_blob, unzip_len, algo = entry

    # UnzipLen: 高 4 位 = 算法 (2=LZMA, 3=ZSTD), 低 28 位 = 解压后大小
    unzip_field = (algo << 28) | (unzip_len & 0x0FFFFFFF)

    blob_pb = (
        _field_varint(1, unzip_field)       # UnzipLen (packed algo|len)
        + _field_varint(2, len(raw_blob))   # BlobLen
        + _field_bytes(3, raw_blob)         # BlobDetail (with LZMA props prefix)
    )

    chunk_save_pb = (
        _field_varint(1, WORLD_OWID)
        + _field_varint(2, WORLD_MAP_ID)
        + _field_sint32(3, cx)
        + _field_sint32(4, cz)
        + _field_varint(5, 1)               # Version
        + _field_varint(6, 0)               # ShareFlag
        + _field_bytes(7, blob_pb)
    )

    chunk_full = (
        _field_varint(1, 0xFFFF)            # SectionFlags
        + _field_varint(2, 1)               # Initialize
        + _field_bytes(3, chunk_save_pb)
    )
    return chunk_full


def _build_room_extra() -> bytes:
    """PB_SYNC_ROOM_EXTRA_HC (cmd 5205) - sent on connect."""
    extra = proto.hc.PB_RoomExtraInfoHC()
    extra.room_extra = json.dumps({
        "audioconfigurl": "",
        "autoTag": "创造",
        "editorSceneSwitch": 1,
        "modUuids": [],
        "modurl": "",
        "translate": "",
        "translate_sourcelang": 0,
        "uilibsurl": "",
        "version": mn2mc.mini.version,
        "vipExp": 0, "vipLevel": 0, "vipType": 0,
        "worldtype": 4,
    }).encode()
    extra.CMURL = "http://prod-env-cloud-maps.mini1.cn/cmcache/72954558563850/53f351d2a6272d2df1c38bf7b4ea9fce"
    extra.MapMD5 = "53f351d2a6272d2df1c38bf7b4ea9fce"
    extra.MapID = 72954558563850
    return extra.SerializeToString()


async def setup_player(player: MiniPlayer) -> None:
    """Send the initial packets to a newly-connected player."""
    # 1. Room extra info
    player.send_packet(
        proto.common.ePBMsgCode.PB_SYNC_ROOM_EXTRA_HC,
        _build_room_extra(),
    )

    # 注: chunks 不在这里发, 移到 enter_world.on_recv (after ENTER_WORLD_HC)
    # 因为客户端要等 world 初始化标志才会处理 chunk

    # 3. Weather (groups 1..7)
    for gid in range(1, 8):
        player.send_packet(
            proto.common.ePBMsgCode.PB_GROUP_WEATHER_HC,
            proto.hc.PB_WeatherHC(
                groupID=gid, weatherID=1, weatherTime=10000
            ).SerializeToString(),
        )

    # 4. Players update
    player.send_packet(
        proto.common.ePBMsgCode.PB_PLAYERS_UPDATEINFO_HC,
        proto.hc.PB_PlayersUpdateInfoHC(
            Players=[proto.common.PB_PlayerBriefInfo(
                Uin=mn2mc.mini.auth.uin,
                NickName="MN2MC Server",
                HP=100,
            )]
        ).SerializeToString(),
    )

    logger.info(f"setup sent to {player.uin}: room_extra + 7 weather + players (chunks deferred)")


def send_all_chunks(player) -> int:
    """在 ENTER_WORLD_HC 之后调用,推送所有 chunk。"""
    sent = 0
    for (cx, cz), _ in _real_chunks.items():
        pkt = _build_chunk_packet_real(cx, cz)
        if pkt is None:
            continue
        player.send_packet(
            proto.common.ePBMsgCode.PB_SYNC_CHUNK_DATA_HC,
            pkt,
        )
        sent += 1
    logger.info(f"sent {sent} chunks to {player.uin} (post-enter)")
    return sent


# ============================================================
# TCP Backend Server
# ============================================================

class BackendServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 19134):
        self.host = host
        self.port = port
        self.players_by_guid: dict[int, MiniPlayer] = {}
        self.writer: asyncio.StreamWriter | None = None
        self._send_lock = asyncio.Lock()

    def send_to_client(self, guid: int, data: bytes) -> None:
        """Called by FakeConnection.send - frame and write to TCP."""
        if not self.writer:
            return
        frame_len = 4 + len(data)
        try:
            self.writer.write(struct.pack("<II", frame_len, guid) + data)
        except Exception as e:
            logger.error(f"send_to_client write failed: {e}")

    async def start(self) -> None:
        srv = await asyncio.start_server(self.handle_proxy, self.host, self.port)
        addr = srv.sockets[0].getsockname()
        logger.info(f"Backend listening on {addr}")
        async with srv:
            await srv.serve_forever()

    async def handle_proxy(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        peer = writer.get_extra_info("peername")
        logger.info(f"C++ proxy connected: {peer}")
        if self.writer is not None:
            logger.warning("Another C++ proxy already connected, replacing.")
            try:
                self.writer.close()
            except Exception:
                pass
        self.writer = writer

        try:
            while True:
                header = await reader.readexactly(8)
                frame_len, client_guid = struct.unpack("<II", header)
                data_len = frame_len - 4
                if data_len < 0 or data_len > 1024 * 1024:
                    logger.error(f"bad frame data_len={data_len}")
                    break
                data = await reader.readexactly(data_len) if data_len > 0 else b""
                await self.dispatch(client_guid, data)
        except asyncio.IncompleteReadError:
            logger.info("C++ proxy disconnected")
        except Exception as e:
            logger.exception(f"backend handler error: {e}")
        finally:
            if self.writer is writer:
                self.writer = None
            for p in list(self.players_by_guid.values()):
                p.kick()
            self.players_by_guid.clear()

    async def dispatch(self, client_guid: int, data: bytes) -> None:
        if len(data) >= 2 and data[0] == 0x00:
            # Control frame
            ctrl = data[1]
            if ctrl == 0x01:
                await self.on_client_connect(client_guid)
            elif ctrl == 0x02:
                await self.on_client_disconnect(client_guid)
            else:
                logger.warning(f"unknown control 0x{ctrl:02x} for {client_guid}")
            return

        # Game data
        player = self.players_by_guid.get(client_guid)
        if player is None:
            logger.warning(f"({client_guid}) game data before connect frame, creating player lazily")
            await self.on_client_connect(client_guid)
            player = self.players_by_guid.get(client_guid)
            if player is None:
                return

        if data[0:1] == b"\x89" and len(data) >= 13:
            try:
                mcp = MiniClientPacket(data)
                logger.info(f"({client_guid}) << code={mcp.msgcode} len={len(mcp.data)}")
                if config.debug:
                    try:
                        protobuf_parser.parse(mcp.msgcode, mcp.data)
                    except Exception:
                        pass
                await on_event(mcp.msgcode, player, mcp)
            except Exception as e:
                logger.exception(f"({client_guid}) packet dispatch error: {e}")
        else:
            logger.warning(f"({client_guid}) non-89 game frame: {data[:32].hex()}")

    async def on_client_connect(self, guid: int) -> None:
        if guid in self.players_by_guid:
            return
        fake_conn = FakeConnection(guid, self)
        player = MiniPlayer(fake_conn, guid)
        self.players_by_guid[guid] = player
        logger.info(f"({guid}) connected via bridge")
        await setup_player(player)
        if config.mini["server"]["host_to_room_server"]:
            try:
                await mn2mc.mini.room.room_update(len(self.players_by_guid))
            except Exception as e:
                logger.warning(f"room_update failed: {e}")

    async def on_client_disconnect(self, guid: int) -> None:
        player = self.players_by_guid.pop(guid, None)
        if player is None:
            return
        try:
            player.kick()
        except Exception:
            pass
        logger.info(f"({guid}) disconnected via bridge")
        if config.mini["server"]["host_to_room_server"]:
            try:
                await mn2mc.mini.room.room_update(len(self.players_by_guid))
            except Exception as e:
                logger.warning(f"room_update failed: {e}")


# ============================================================
# Main
# ============================================================

async def main():
    import os
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "backend_{time:YYYY-MM-DD_HH-mm-ss}.log")
    logger.add(log_path, level="DEBUG", rotation="50 MB", encoding="utf-8")
    logger.info(f"Log file: {log_path}")
    config.load()

    if config.debug:
        protobuf_parser.init()

    logger.info("=== MN2MC Backend (TCP bridge :19134 → mn2mc_proxy) ===")

    # Step 1: auth + create room (HTTP/WSS, like room_only.py)
    await mn2mc.mini.wsconn.fetch_s2()
    await mn2mc.mini.room.create_room()
    logger.info(f"Room ready. Host UID: {mn2mc.mini.auth.uin}")
    logger.info(f"Start mn2mc_proxy with: --mode dual --port 19132 --host-port 19133 "
                f"--guid {mn2mc.mini.auth.uin} --backend 127.0.0.1:19134 --lan-ip "
                f"{config.mini['server'].get('lan_ip', '192.168.1.7')}")

    # Step 2: load aiorak event handlers (enter_world, chat, move, etc.)
    mini_load_all_event()

    # Step 2b: 加载真实 chunk 缓存
    n = _load_real_chunks()
    logger.info(f"Loaded {n} real chunks from cachetrunk for world {WORLD_OWID}")
    if n == 0:
        logger.warning(f"No chunks found under {CHUNK_CACHE_ROOT}, falling back to empty void")

    # Step 3: start TCP backend
    backend = BackendServer()
    try:
        await backend.start()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        if config.mini["server"]["host_to_room_server"]:
            try:
                await mn2mc.mini.room.close_room()
            except Exception:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
