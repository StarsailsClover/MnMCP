"""
全端口嗅探: 同时监听 80 + 443 + 8080
443 用自签证书的 TLS
另外用 asyncio 监控系统 DNS 查询和 TCP 连接
"""
import asyncio
import ssl
import sys
import os
import subprocess
import tempfile
from aiohttp import web

HIT = False

async def handle(request: web.Request):
    global HIT
    HIT = True
    body = await request.text()
    scheme = "HTTPS" if request.secure else "HTTP"
    port = request.url.port or (443 if request.secure else 80)
    print(f"\n{'='*60}")
    print(f"[{scheme}:{port}] {request.remote} -> {request.method} {request.path_qs}")
    print(f"  Host: {request.headers.get('Host', '?')}")
    for k, v in request.headers.items():
        if k.lower() not in ('host',):
            print(f"  {k}: {v[:100]}")
    if body:
        print(f"  Body({len(body)}): {body[:300]}")
    print(f"{'='*60}\n")
    return web.Response(status=200, text='{"code":0}')


def make_self_signed_cert():
    """生成临时自签证书"""
    certfile = os.path.join(tempfile.gettempdir(), "mn2mc_sniff.pem")
    keyfile = os.path.join(tempfile.gettempdir(), "mn2mc_sniff.key")
    if os.path.exists(certfile) and os.path.exists(keyfile):
        return certfile, keyfile
    try:
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", keyfile, "-out", certfile,
            "-days", "1", "-nodes",
            "-subj", "/CN=cs-gsmgr.mini1.cn"
        ], check=True, capture_output=True, timeout=10)
        return certfile, keyfile
    except Exception as e:
        print(f"openssl 不可用({e}), 443 监听跳过")
        return None, None


async def raw_tcp_handler(reader, writer):
    """原始 TCP 嗅探 (用于 443 没有 TLS 时)"""
    addr = writer.get_extra_info('peername')
    port = writer.get_extra_info('sockname')[1]
    data = await asyncio.wait_for(reader.read(4096), timeout=5)
    print(f"\n{'='*60}")
    print(f"[RAW TCP:{port}] {addr} -> {len(data)} bytes")
    print(f"  Hex: {data[:64].hex()}")
    try:
        print(f"  Text: {data[:200].decode('utf-8', errors='replace')}")
    except:
        pass
    # 检查是不是 TLS ClientHello
    if data and data[0] == 0x16:
        print(f"  >>> 这是 TLS ClientHello! 客户端用的 HTTPS!")
        # 尝试提取 SNI
        try:
            sni = extract_sni(data)
            if sni:
                print(f"  >>> SNI (域名): {sni}")
        except:
            pass
    print(f"{'='*60}\n")
    writer.close()


def extract_sni(data: bytes) -> str:
    """从 TLS ClientHello 提取 SNI"""
    if len(data) < 43:
        return ""
    # Skip: type(1) + version(2) + length(2) + handshake_type(1) + length(3) + version(2)
    pos = 43  # after session_id_length position
    if pos >= len(data):
        return ""
    session_id_len = data[pos]
    pos += 1 + session_id_len
    if pos + 2 >= len(data):
        return ""
    cipher_suites_len = int.from_bytes(data[pos:pos+2], 'big')
    pos += 2 + cipher_suites_len
    if pos >= len(data):
        return ""
    comp_methods_len = data[pos]
    pos += 1 + comp_methods_len
    if pos + 2 >= len(data):
        return ""
    extensions_len = int.from_bytes(data[pos:pos+2], 'big')
    pos += 2
    end = pos + extensions_len
    while pos + 4 < end and pos < len(data):
        ext_type = int.from_bytes(data[pos:pos+2], 'big')
        ext_len = int.from_bytes(data[pos+2:pos+4], 'big')
        pos += 4
        if ext_type == 0:  # SNI
            if pos + 5 < len(data):
                name_len = int.from_bytes(data[pos+3:pos+5], 'big')
                if pos + 5 + name_len <= len(data):
                    return data[pos+5:pos+5+name_len].decode('ascii', errors='replace')
        pos += ext_len
    return ""


async def monitor_connections():
    """定期打印迷你世界进程的网络连接"""
    print("\n监控迷你世界进程的网络连接...\n")
    seen = set()
    while True:
        await asyncio.sleep(2)
        try:
            out = subprocess.check_output(
                'netstat -ano | findstr "mini" || echo none',
                shell=True, text=True, timeout=5, stderr=subprocess.DEVNULL
            )
            # 也试 Mini 进程名
            out2 = subprocess.check_output(
                'tasklist /FI "IMAGENAME eq Mini*" /FO CSV /NH 2>NUL || echo none',
                shell=True, text=True, timeout=5, stderr=subprocess.DEVNULL
            )

            pids = set()
            for line in out2.strip().splitlines():
                if "Mini" in line and "," in line:
                    parts = line.strip('"').split('","')
                    if len(parts) >= 2:
                        try:
                            pids.add(parts[1])
                        except:
                            pass

            if pids:
                for pid in pids:
                    try:
                        netout = subprocess.check_output(
                            f'netstat -ano | findstr {pid}',
                            shell=True, text=True, timeout=5, stderr=subprocess.DEVNULL
                        )
                        for line in netout.strip().splitlines():
                            line = line.strip()
                            if line and line not in seen and ("ESTABLISHED" in line or "SYN_SENT" in line):
                                seen.add(line)
                                print(f"[NETSTAT] {line}")
                    except:
                        pass
        except:
            pass


async def main():
    print("=" * 60)
    print("全端口嗅探器")
    print("=" * 60)
    print(f"监听: HTTP(80) + HTTPS/RAW(443) + HTTP(8080)")
    print(f"hosts 确保: 192.168.1.233 cs-gsmgr.mini1.cn")
    print(f"启动迷你世界, 加入房间, 看这里有没有输出")
    print("=" * 60)
    print()

    app = web.Application()
    app.router.add_route('*', '/{path:.*}', handle)
    runner = web.AppRunner(app)
    await runner.setup()

    # HTTP :80
    try:
        site80 = web.TCPSite(runner, "0.0.0.0", 80)
        await site80.start()
        print("[OK] HTTP :80 启动")
    except OSError as e:
        print(f"[!!] :80 失败: {e}")

    # HTTP :8080 备用
    try:
        site8080 = web.TCPSite(runner, "0.0.0.0", 8080)
        await site8080.start()
        print("[OK] HTTP :8080 启动")
    except OSError as e:
        print(f"[!!] :8080 失败: {e}")

    # HTTPS :443 (自签证书)
    certfile, keyfile = make_self_signed_cert()
    if certfile:
        try:
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_ctx.load_cert_chain(certfile, keyfile)
            site443 = web.TCPSite(runner, "0.0.0.0", 443, ssl_context=ssl_ctx)
            await site443.start()
            print("[OK] HTTPS :443 启动 (自签证书)")
        except OSError as e:
            print(f"[!!] :443 TLS失败: {e}, 改用原始TCP嗅探")
            srv = await asyncio.start_server(raw_tcp_handler, "0.0.0.0", 443)
            print("[OK] RAW TCP :443 启动 (嗅探 TLS ClientHello)")
    else:
        # 没有 openssl, 用原始 TCP 嗅探
        try:
            srv = await asyncio.start_server(raw_tcp_handler, "0.0.0.0", 443)
            print("[OK] RAW TCP :443 启动 (嗅探模式)")
        except OSError as e:
            print(f"[!!] :443 失败: {e}")

    print()
    print("等待迷你世界请求...")
    print("同时监控迷你世界进程的网络连接")
    print()

    # 后台监控 netstat
    asyncio.create_task(monitor_connections())

    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n退出")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
