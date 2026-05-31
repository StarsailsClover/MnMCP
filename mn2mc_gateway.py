"""
MN2MC Gateway - HTTP proxy + RakNet game server
Proxifier routes MiniWorld traffic through us.
We intercept /v2/room/get and return our own IP:port.
Everything else passes through to real servers.
"""
import asyncio
import struct
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(__file__))
os.environ["PYTHONIOENCODING"] = "utf-8"

import aiohttp
import aiorak
from aiohttp import web
from loguru import logger

# Lazy imports to avoid JS bridge
import mn2mc.config as config
import mn2mc.mini.proto as proto
from mn2mc.mini.msgcode_registry import get_name, get_direction, get_message_class, _CODE_TO_NAME
from mn2mc.mini.packet import MiniServerPacket

LOCAL_IP = "192.168.1.7"
RAKNET_PORT = 19132
HTTP_PROXY_PORT = 8899

logger.remove()
logger.add(sys.stderr, level="DEBUG",
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level:7s}</level> | <cyan>{extra[tag]:>6s}</cyan> | {message}")

hlog = logger.bind(tag="HTTP")
rlog = logger.bind(tag="RAKNET")
plog = logger.bind(tag="PROTO")
glog = logger.bind(tag="MAIN")

FAKE_ROOM = {
    "code": 0, "msg": "found",
    "aid": "99999999999999", "roomid": "mn2mc_test",
    "ip": LOCAL_IP, "port": RAKNET_PORT,
    "room_cap": 10, "player_num": 0,
    "mod_url": "", "room_mods": "", "room_ui_libs": "",
    "room_ver": "1.56.0", "room_name": "MN2MC Gateway",
    "room_audio_config": json.dumps({"editorSceneSwitch": 1, "worldtype": 4}),
    "room_translate": "", "czb_uuid": "",
    "uin": 1000, "nick_name": "MN2MC", "is_cloud": False,
    "passwd_md5": "", "share_version": str(int(time.time())),
    "team_id": 0, "public_type": 0, "can_trace": 0, "personal": 0,
    "teams": [{"team_id": 0, "cap": 40, "uin_list": ["1000"]}],
    "room_from": "", "not_follow": False,
}

# ============================================================
# HTTP Proxy (for Proxifier)
# ============================================================
async def handle_proxy_request(request: web.Request):
    url = str(request.url)
    host = request.headers.get("Host", "")

    # Intercept room/get
    if "cs-gsmgr" in host and "/v2/room/get" in request.path:
        body = await request.text()
        hlog.info(f">>> INTERCEPT {request.method} {request.path}")
        hlog.info(f"<<< Return fake room -> {LOCAL_IP}:{RAKNET_PORT}")
        return web.json_response(FAKE_ROOM)

    # Pass through everything else
    try:
        target_url = url
        body = await request.read()
        headers = {k: v for k, v in request.headers.items()
                   if k.lower() not in ('host', 'transfer-encoding')}

        async with aiohttp.ClientSession() as session:
            async with session.request(
                request.method, target_url,
                headers=headers, data=body,
                timeout=aiohttp.ClientTimeout(total=15),
                ssl=False,
            ) as resp:
                resp_body = await resp.read()
                resp_headers = {k: v for k, v in resp.headers.items()
                               if k.lower() not in ('transfer-encoding', 'content-encoding', 'content-length')}
                return web.Response(status=resp.status, body=resp_body, headers=resp_headers)
    except Exception as e:
        hlog.warning(f"Proxy error for {url[:80]}: {e}")
        return web.Response(status=502, text=str(e))

# ============================================================
# RakNet Game Server (S2C 5-byte format like real cloud server)
# ============================================================
async def raknet_handler(conn: aiorak.Connection):
    remote = conn.remote_address
    guid = conn.remote_guid
    rlog.info(f"=== CONNECTED === guid={guid} addr={remote}")

    # Send PB_SYNC_ROOM_EXTRA_HC immediately (5-byte S2C format)
    extra = proto.hc.PB_RoomExtraInfoHC()
    extra.room_extra = json.dumps({
        "audioconfigurl": "",
        "autoTag": "MN2MC",
        "editorSceneSwitch": 1,
        "modUuids": [], "modurl": "", "translate": "",
        "translate_sourcelang": 0, "uilibsurl": "",
        "version": "1.56.0",
        "vipExp": 0, "vipLevel": 0, "vipType": 0,
        "worldtype": 4,
    }).encode()
    extra_bytes = extra.SerializeToString()

    pkt = MiniServerPacket(
        proto.common.ePBMsgCode.PB_SYNC_ROOM_EXTRA_HC,
        extra_bytes
    ).encode()
    conn.send(pkt, aiorak.Reliability.RELIABLE_ORDERED)
    rlog.info(f">> PB_SYNC_ROOM_EXTRA_HC ({len(extra_bytes)}B)")

    count = 0
    try:
        async for data in conn:
            count += 1

            # Non-game packet
            if len(data) < 13 or data[0:1] != b'\x89':
                rlog.info(f"[{count}] non-game ({len(data)}B): {data.hex()}")
                continue

            # Parse C2S: 89 + UIN(4B BE) + PLACEHOLDER(4B) + CODE(2B LE) + LEN(2B LE) + DATA
            uin = struct.unpack_from(">I", data, 1)[0]
            msgcode = struct.unpack_from("<H", data, 9)[0]
            length = struct.unpack_from("<H", data, 11)[0]
            pkt_data = data[13:13 + length]
            name = get_name(msgcode) or f"UNK_{msgcode}"

            plog.info(f"[{count}] << uin={uin} code={msgcode} {name} ({length}B)")

            # Decode proto
            cls = get_message_class(msgcode)
            if cls and pkt_data:
                try:
                    msg = cls()
                    msg.ParseFromString(pkt_data)
                    for fd in msg.DESCRIPTOR.fields:
                        try:
                            if msg.HasField(fd.name):
                                val = getattr(msg, fd.name)
                                if isinstance(val, bytes):
                                    plog.debug(f"       {fd.name} = {len(val)}B")
                                elif isinstance(val, (int, float, bool, str)):
                                    plog.debug(f"       {fd.name} = {val}")
                        except ValueError:
                            pass
                except Exception as e:
                    plog.warning(f"       proto parse error: {e}")

            # Handle specific packets
            if msgcode == 1013:  # PB_ROLE_CHECK_JOINFROMSRC_CH
                rlog.info(f"*** Client sent JOINFROMSRC! Connection working! ***")

            elif msgcode == 1001:  # PB_ROLE_ENTER_WORLD_CH
                rlog.info(f"*** Client sent ENTER_WORLD! SUCCESS! ***")

            elif msgcode == 11:  # PB_HEARTBEAT_CH
                # Reply heartbeat
                hb_reply = proto.hc.PB_HeartBeatHC(BeatCode=0).SerializeToString()
                conn.send(MiniServerPacket(
                    proto.common.ePBMsgCode.PB_HEARTBEAT_HC, hb_reply
                ).encode(), aiorak.Reliability.RELIABLE_ORDERED)

    except Exception as e:
        rlog.info(f"Connection closed: {e}")

    rlog.info(f"=== DISCONNECTED === guid={guid} packets={count}")


# ============================================================
# Main
# ============================================================
async def main():
    os.makedirs("logs", exist_ok=True)
    config.load()

    glog.info("=" * 60)
    glog.info("MN2MC Gateway")
    glog.info("=" * 60)
    glog.info(f"HTTP Proxy: 0.0.0.0:{HTTP_PROXY_PORT}")
    glog.info(f"RakNet:     0.0.0.0:{RAKNET_PORT}")
    glog.info(f"Proto:      {len(_CODE_TO_NAME)} codes")
    glog.info("")
    glog.info("Proxifier setup:")
    glog.info(f"  1. Add proxy: HTTP 127.0.0.1:{HTTP_PROXY_PORT}")
    glog.info(f"  2. Add rule: MiniWorld.exe -> use this proxy")
    glog.info(f"  3. Search UID in MiniWorld and join any room")
    glog.info("=" * 60)

    # Start HTTP proxy
    app = web.Application()
    app.router.add_route('*', '/{path:.*}', handle_proxy_request)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", HTTP_PROXY_PORT)
    await site.start()
    hlog.info(f"HTTP proxy started on :{HTTP_PROXY_PORT}")

    # Start RakNet server
    server = await aiorak.create_server(
        ("0.0.0.0", RAKNET_PORT),
        raknet_handler,
        guid=666,
    )
    rlog.info(f"RakNet server started on :{RAKNET_PORT}")

    glog.info("")
    glog.info(">>> Gateway ready! <<<")
    glog.info("")

    try:
        await server.serve_forever()
    except KeyboardInterrupt:
        glog.info("Shutting down...")
    finally:
        await server.close()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
