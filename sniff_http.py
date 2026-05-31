"""
极简 HTTP 嗅探器: 监听 80 端口，打印所有收到的请求，全部返回 502
用来确认客户端到底有没有请求到我们、请求了什么路径
"""
import asyncio
from aiohttp import web

async def handle(request: web.Request):
    body = await request.text()
    print(f"\n{'='*60}")
    print(f"[{request.remote}] {request.method} {request.url}")
    print(f"Host: {request.headers.get('Host', '?')}")
    print(f"Headers: {dict(request.headers)}")
    if body:
        print(f"Body({len(body)}): {body[:500]}")
    print(f"{'='*60}\n")
    return web.Response(status=502, text="sniff only")

app = web.Application()
app.router.add_route('*', '/{path:.*}', handle)

if __name__ == "__main__":
    print("HTTP 嗅探器启动在 0.0.0.0:80")
    print("确保 hosts: 192.168.1.233 cs-gsmgr.mini1.cn")
    print("启动迷你世界，观察有没有请求过来\n")
    web.run_app(app, host="0.0.0.0", port=80, print=None)
