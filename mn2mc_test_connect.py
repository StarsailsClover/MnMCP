"""
MN2MC 实际连接测试工具 v2
=========================
反向代理模式: 只劫持 /v2/room/get，其余全部透传真实服务器

使用:
  1. 关 Clash
  2. hosts 文件加: 192.168.1.233 cs-gsmgr.mini1.cn
  3. python mn2mc_test_connect.py
  4. 正常启动迷你世界, 加入任意房间
"""
import asyncio
import json
import struct
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

import aiohttp
import aiorak
from aiohttp import web
from loguru import logger

from mn2mc.mini.msgcode_registry import (
    get_name, get_direction, get_message_class, _CODE_TO_NAME
)
import mn2mc.mini.proto as proto

LOCAL_IP = "192.168.1.233"
RAKNET_PORT = 19132
HTTP_PORT = 80
REAL_SERVER = "cs-gsmgr.mini1.cn"
REAL_SERVER_IP_FALLBACK = "60.204.1.188"

logger.remove()
logger.add(sys.stderr, level="DEBUG",
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level:7s}</level> | <cyan>{extra[tag]:>6s}</cyan> | {message}")
logger.add("logs/connect_test_{time}.log", level="DEBUG", rotation="50 MB")

http_log = logger.bind(tag="HTTP")
rak_log = logger.bind(tag="RAKNET")
proto_log = logger.bind(tag="PROTO")
gen_log = logger.bind(tag="MAIN")

CAPTURED = []

# ============================================================
# HTTP 反向代理 — 只劫持 /v2/room/get
# ============================================================
FAKE_ROOM = {
    "code": 0, "msg": "found",
    "aid": "99999999999999", "roomid": "mn2mc_test",
    "ip": LOCAL_IP, "port": RAKNET_PORT,
    "room_cap": 10, "player_num": 0,
    "mod_url": "", "room_mods": "", "room_ui_libs": "",
    "room_ver": "1.55.0", "room_name": "MN2MC Test",
    "room_audio_config": json.dumps({"editorSceneSwitch": 1, "worldtype": 4}),
    "room_translate": "", "czb_uuid": "",
    "uin": 1000, "nick_name": "MN2MC", "is_cloud": False,
    "passwd_md5": "", "share_version": str(int(time.time())),
    "team_id": 0, "public_type": 0, "can_trace": 0, "personal": 0,
    "teams": [{"team_id": 0, "cap": 40, "uin_list": ["1000"]}],
    "room_from": "", "not_follow": False,
}

UPSTREAM_SESSION: aiohttp.ClientSession = None

async def get_upstream_session():
    global UPSTREAM_SESSION
    if UPSTREAM_SESSION is None or UPSTREAM_SESSION.closed:
        # 用 DNS 直连真实 IP，绕过 hosts 劫持
        resolver = aiohttp.resolver.AsyncResolver()
        # 先手动解析真实 IP（脚本启动时做一次）
        UPSTREAM_SESSION = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        )
    return UPSTREAM_SESSION


async def proxy_to_upstream(request: web.Request):
    """透传请求到真实 cs-gsmgr.mini1.cn"""
    session = await get_upstream_session()
    target_url = f"http://{REAL_SERVER_IP}{request.path_qs}"

    try:
        body = await request.read()
        headers = dict(request.headers)
        headers.pop("Host", None)
        headers["Host"] = REAL_SERVER

        async with session.request(
            request.method, target_url,
            headers=headers, data=body,
            timeout=aiohttp.ClientTimeout(total=15)
        ) as resp:
            resp_body = await resp.read()
            return web.Response(
                status=resp.status,
                body=resp_body,
                headers={k: v for k, v in resp.headers.items()
                         if k.lower() not in ('transfer-encoding', 'content-encoding')}
            )
    except Exception as e:
        http_log.error(f"代理失败: {e}")
        return web.Response(status=502, text=f"proxy error: {e}")


async def handle_request(request: web.Request):
    path = request.path

    # 劫持: 加入房间
    if path in ("/v2/room/get", "/v2/rent_room/get"):
        body = await request.text()
        http_log.info(f">>> 劫持 {request.method} {path}")
        if body:
            http_log.debug(f"    Body: {body[:300]}")
        http_log.info(f"<<< 返回假房间 -> {LOCAL_IP}:{RAKNET_PORT}")
        return web.json_response(FAKE_ROOM)

    # 其他: 透传
    http_log.debug(f"--- 透传 {request.method} {path}")
    return await proxy_to_upstream(request)


# ============================================================
# RakNet 包解析
# ============================================================
def parse_client_packet(raw: bytes):
    if len(raw) < 13 or raw[0:1] != b'\x89':
        return None, None, None, raw
    uin = struct.unpack(">I", raw[1:5])[0]
    msgcode, length = struct.unpack("<HH", raw[9:13])
    data = raw[13:13 + length]
    return uin, msgcode, length, data


def format_proto_fields(msg) -> dict:
    fields = {}
    for fd in msg.DESCRIPTOR.fields:
        try:
            if msg.HasField(fd.name):
                val = getattr(msg, fd.name)
                if isinstance(val, bytes):
                    fields[fd.name] = val[:64].hex() + ("..." if len(val) > 64 else "")
                elif isinstance(val, (int, float, bool, str)):
                    fields[fd.name] = val
                else:
                    fields[fd.name] = str(val)[:200]
        except ValueError:
            val = getattr(msg, fd.name)
            if fd.label == fd.LABEL_REPEATED and len(val) > 0:
                fields[fd.name] = f"[{len(val)} items]"
    return fields


# ============================================================
# RakNet 服务器
# ============================================================
async def raknet_handler(conn: aiorak.Connection):
    remote = conn.remote_address
    guid = conn.remote_guid
    rak_log.info(f"========== 新连接 ==========")
    rak_log.info(f"  GUID: {guid}  地址: {remote}")

    extra = proto.hc.PB_RoomExtraInfoHC()
    extra.room_extra = json.dumps({
        "audioconfigurl": json.dumps({"editorSceneSwitch": 1, "worldtype": 4}),
        "autoTag": "综合", "editorSceneSwitch": 0,
        "modUuids": [], "modurl": "", "translate": "",
        "translate_sourcelang": 0, "uilibsurl": "",
        "version": "1.55.0",
        "vipExp": 0, "vipLevel": 0, "vipType": 0,
    }).encode()
    extra_bytes = extra.SerializeToString()
    pkt = b'\x89' + struct.pack("<HH", 5205, len(extra_bytes)) + extra_bytes
    conn.send(pkt, aiorak.Reliability.RELIABLE_ORDERED)
    rak_log.info(f">> PB_SYNC_ROOM_EXTRA_HC ({len(extra_bytes)}B)")

    count = 0
    try:
        async for raw in conn:
            count += 1
            uin, code, length, data = parse_client_packet(raw)
            if code is None:
                rak_log.warning(f"[{count:04d}] 非标准包 ({len(raw)}B): {raw[:32].hex()}")
                continue

            name = get_name(code) or f"UNK_{code}"
            direction = get_direction(code)
            cls = get_message_class(code)
            proto_log.info(f"[{count:04d}] uin={uin} {code:5d} {name} ({direction}) {length}B")

            if cls and data:
                try:
                    msg = cls()
                    msg.ParseFromString(data)
                    for k, v in format_proto_fields(msg).items():
                        proto_log.debug(f"       {k} = {v}")
                except Exception as e:
                    proto_log.warning(f"       解析失败: {e}")

            CAPTURED.append({
                "seq": count, "time": datetime.now().isoformat(),
                "uin": uin, "code": code, "name": name,
                "direction": direction, "length": length,
                "data_hex": data.hex() if data else "",
            })

    except aiorak.ConnectionClosedError:
        rak_log.info(f"连接关闭 guid={guid}")
    except Exception as e:
        rak_log.exception(f"异常: {e}")

    rak_log.info(f"断开 guid={guid} 共 {count} 包")
    if CAPTURED:
        p = f"logs/packets_{guid}_{int(time.time())}.json"
        with open(p, "w", encoding="utf-8") as f:
            json.dump(CAPTURED, f, indent=2, ensure_ascii=False)
        rak_log.info(f"已保存 {p}")


# ============================================================
# main
# ============================================================
REAL_SERVER_IP = None

async def resolve_real_ip():
    """启动时解析真实 IP，后续直连不走 hosts"""
    global REAL_SERVER_IP
    import socket
    try:
        REAL_SERVER_IP = socket.getaddrinfo(REAL_SERVER, 80, socket.AF_INET)[0][4][0]
    except Exception:
        REAL_SERVER_IP = None

    if REAL_SERVER_IP and REAL_SERVER_IP == LOCAL_IP:
        gen_log.warning(f"DNS 解析到本机! hosts 已生效但需要真实 IP")
        gen_log.info(f"尝试用备用 DNS 解析...")
        import subprocess
        try:
            out = subprocess.check_output(
                ["nslookup", REAL_SERVER, "223.5.5.5"],
                timeout=5, text=True, stderr=subprocess.DEVNULL
            )
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("Address") and "223.5.5.5" not in line:
                    ip = line.split(":")[-1].strip()
                    if ip and ip != LOCAL_IP:
                        REAL_SERVER_IP = ip
                        break
        except Exception:
            pass

    if not REAL_SERVER_IP or REAL_SERVER_IP == LOCAL_IP or REAL_SERVER_IP == "127.0.0.1":
        REAL_SERVER_IP = REAL_SERVER_IP_FALLBACK
        gen_log.info(f"DNS 被劫持, 使用备用真实 IP: {REAL_SERVER_IP}")
    else:
        gen_log.info(f"{REAL_SERVER} 真实 IP: {REAL_SERVER_IP}")


async def main():
    os.makedirs("logs", exist_ok=True)

    gen_log.info("=" * 60)
    gen_log.info("MN2MC 连接测试 v2 (反向代理模式)")
    gen_log.info("=" * 60)

    await resolve_real_ip()

    gen_log.info(f"本机: {LOCAL_IP}  RakNet: {RAKNET_PORT}  HTTP: {HTTP_PORT}")
    gen_log.info(f"上游: {REAL_SERVER} -> {REAL_SERVER_IP}")
    gen_log.info(f"Proto: {len(_CODE_TO_NAME)} codes (659 有类)")
    gen_log.info("")
    gen_log.info("确保 hosts 文件有:")
    gen_log.info(f"  {LOCAL_IP} cs-gsmgr.mini1.cn")
    gen_log.info("然后正常启动迷你世界, 搜索/加入任意房间")
    gen_log.info("=" * 60)

    app = web.Application()
    app.router.add_route('*', '/{path:.*}', handle_request)
    runner = web.AppRunner(app)
    await runner.setup()

    try:
        site = web.TCPSite(runner, "0.0.0.0", HTTP_PORT)
        await site.start()
        http_log.info(f"HTTP 反代启动: 0.0.0.0:{HTTP_PORT}")
    except OSError as e:
        http_log.error(f"端口 {HTTP_PORT} 被占用: {e}")
        http_log.info("尝试 8080...")
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()
        http_log.warning(f"HTTP 在 8080, hosts 方案不可用, 需要额外端口转发")

    server = await aiorak.create_server(
        ("0.0.0.0", RAKNET_PORT), raknet_handler, guid=666
    )
    rak_log.info(f"RakNet 启动: 0.0.0.0:{RAKNET_PORT}")

    gen_log.info("")
    gen_log.info(">>> 就绪, 等待连接... <<<")
    gen_log.info("")

    try:
        await server.serve_forever()
    except KeyboardInterrupt:
        gen_log.info("关闭中...")
    finally:
        await server.close()
        if UPSTREAM_SESSION and not UPSTREAM_SESSION.closed:
            await UPSTREAM_SESSION.close()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
