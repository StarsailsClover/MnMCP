"""
MnMCP v3 - HTTP 代理模块
移植自 MnMCP-MN2MC，改进架构和代码质量

功能:
1. HTTP 反向代理 - 劫持 /v2/room/get
2. 返回自定义 IP:端口，引导 MiniWorld 连接到本地
3. 其余请求透传到真实服务器
"""

import asyncio
import json
import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

from aiohttp import web, ClientSession
from aiohttp.web_middlewares import middleware

logger = logging.getLogger(__name__)


class ProxyMode(Enum):
    """代理模式"""
    TRANSPARENT = "transparent"  # 完全透传
    HIJACK_ROOM = "hijack_room"   # 劫持房间获取
    FULL_PROXY = "full_proxy"     # 完全代理（待实现）


@dataclass
class FakeRoomConfig:
    """假房间配置"""
    aid: str = "99999999999999"
    roomid: str = "mnmcp_test"
    room_name: str = "MnMCP Test Room"
    room_ver: str = "1.56.0"
    room_cap: int = 10
    player_num: int = 0
    uin: int = 1000
    nick_name: str = "MnMCP"
    is_cloud: bool = False
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProxyConfig:
    """代理配置"""
    # 本地监听
    local_ip: str = "127.0.0.1"
    http_port: int = 8899
    
    # RakNet 游戏端口
    raknet_port: int = 19132
    
    # 真实服务器
    real_server: str = "cs-gsmgr.mini1.cn"
    real_server_port: int = 80
    
    # 模式
    mode: ProxyMode = ProxyMode.HIJACK_ROOM
    
    # 假房间配置
    fake_room: FakeRoomConfig = field(default_factory=FakeRoomConfig)
    
    # 调试
    debug: bool = False
    log_requests: bool = True


class MCPHTTPProxy:
    """
    MnMCP HTTP 代理
    
    移植自 MnMCP-MN2MC，改进:
    - 高质量架构
    - 类型注解完整
    - 支持多种代理模式
    - 完善的日志
    
    使用示例:
        config = ProxyConfig(local_ip="192.168.1.100")
        proxy = MCPHTTPProxy(config)
        await proxy.start()
    """
    
    def __init__(self, config: Optional[ProxyConfig] = None):
        """
        初始化代理
        
        Args:
            config: 代理配置
        """
        self.config = config or ProxyConfig()
        self.app: Optional[web.Application] = None
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        self.session: Optional[ClientSession] = None
        
        # 统计
        self.stats = {
            'requests_total': 0,
            'requests_hijacked': 0,
            'requests_passed': 0,
            'errors': 0,
        }
    
    async def start(self) -> None:
        """启动代理"""
        try:
            # 创建 HTTP 会话
            self.session = ClientSession()
            
            # 创建应用
            self.app = web.Application()
            self.app.router.add_get('/v2/room/get', self._handle_room_get)
            self.app.router.add_route('*', '/{path:.*}', self._handle_proxy)
            
            # 添加中间件
            self.app.middlewares.append(self._logging_middleware)
            
            # 启动
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(
                self.runner,
                host=self.config.local_ip,
                port=self.config.http_port
            )
            
            await self.site.start()
            
            logger.info(
                f"HTTP Proxy started on http://{self.config.local_ip}:{self.config.http_port}"
            )
            logger.info(f"Mode: {self.config.mode.value}")
            logger.info(f"RakNet port: {self.config.raknet_port}")
            
        except Exception as e:
            logger.error(f"Failed to start proxy: {e}")
            raise
    
    async def stop(self) -> None:
        """停止代理"""
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            if self.session:
                await self.session.close()
            
            logger.info("HTTP Proxy stopped")
            
        except Exception as e:
            logger.error(f"Error stopping proxy: {e}")
    
    async def _logging_middleware(self, app, handler):
        """日志中间件"""
        async def middleware(request):
            start_time = time.time()
            self.stats['requests_total'] += 1
            
            if self.config.log_requests:
                logger.debug(f"{request.method} {request.path}")
            
            try:
                response = await handler(request)
                elapsed = time.time() - start_time
                logger.debug(f"Response: {response.status} ({elapsed:.3f}s)")
                return response
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Error handling {request.path}: {e}")
                raise
        
        return middleware
    
    async def _handle_room_get(self, request: web.Request) -> web.Response:
        """
        处理房间获取请求 (劫持)
        
        返回假房间信息，引导 MiniWorld 连接到本地 RakNet
        """
        try:
            # 获取原始请求参数
            params = request.query
            logger.info(f"Hijacking room get request: {dict(params)}")
            
            # 构建假房间响应
            room_data = self._build_fake_room_response()
            
            self.stats['requests_hijacked'] += 1
            
            return web.json_response(room_data)
            
        except Exception as e:
            logger.error(f"Error handling room get: {e}")
            return web.json_response(
                {"code": -1, "msg": f"Proxy error: {str(e)}"},
                status=500
            )
    
    async def _handle_proxy(self, request: web.Request) -> web.Response:
        """
        处理其他请求 (透传)
        
        将请求转发到真实服务器
        """
        try:
            target_url = f"http://{self.config.real_server}:{self.config.real_server_port}{request.path}"
            
            # 读取请求体
            body = await request.read() if request.can_read_body else None
            
            # 转发请求
            async with self.session.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers.items() if k.lower() != 'host'},
                params=request.query,
                data=body,
                allow_redirects=False
            ) as response:
                
                # 读取响应
                response_body = await response.read()
                
                # 构建响应
                return web.Response(
                    body=response_body,
                    status=response.status,
                    headers={k: v for k, v in response.headers.items() if k.lower() not in ['transfer-encoding', 'content-encoding']}
                )
                
        except Exception as e:
            logger.error(f"Error proxying {request.path}: {e}")
            return web.json_response(
                {"code": -1, "msg": f"Proxy error: {str(e)}"},
                status=502
            )
    
    def _build_fake_room_response(self) -> Dict[str, Any]:
        """构建假房间响应"""
        cfg = self.config.fake_room
        
        return {
            "code": 0,
            "msg": "found",
            "aid": cfg.aid,
            "roomid": cfg.roomid,
            "ip": self.config.local_ip,
            "port": self.config.raknet_port,
            "room_cap": cfg.room_cap,
            "player_num": cfg.player_num,
            "mod_url": "",
            "room_mods": "",
            "room_ui_libs": "",
            "room_ver": cfg.room_ver,
            "room_name": cfg.room_name,
            "room_audio_config": json.dumps({"editorSceneSwitch": 1, "worldtype": 4}),
            "room_translate": "",
            "czb_uuid": "",
            "uin": cfg.uin,
            "nick_name": cfg.nick_name,
            "is_cloud": cfg.is_cloud,
            "passwd_md5": "",
            "share_version": str(int(time.time())),
            "team_id": 0,
            "public_type": 0,
            "can_trace": 0,
            "personal": 0,
            "teams": [{
                "team_id": 0,
                "cap": 40,
                "uin_list": [str(cfg.uin)]
            }],
            "room_from": "",
            "not_follow": False,
            **cfg.custom_data
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            'local_ip': self.config.local_ip,
            'http_port': self.config.http_port,
            'raknet_port': self.config.raknet_port,
            'mode': self.config.mode.value,
        }


# 便捷函数
async def start_proxy(
    local_ip: str = "127.0.0.1",
    http_port: int = 8899,
    raknet_port: int = 19132
) -> MCPHTTPProxy:
    """
    快速启动代理
    
    Args:
        local_ip: 本地IP
        http_port: HTTP端口
        raknet_port: RakNet端口
        
    Returns:
        代理实例
    """
    config = ProxyConfig(
        local_ip=local_ip,
        http_port=http_port,
        raknet_port=raknet_port
    )
    proxy = MCPHTTPProxy(config)
    await proxy.start()
    return proxy


# 测试
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("MnMCP v3 - HTTP 代理测试")
    print("=" * 60)
    
    async def test():
        # 创建代理
        config = ProxyConfig(
            local_ip="127.0.0.1",
            http_port=8899,
            raknet_port=19132,
            debug=True
        )
        
        proxy = MCPHTTPProxy(config)
        
        try:
            # 启动
            await proxy.start()
            print(f"\n✓ 代理已启动")
            print(f"  HTTP: http://127.0.0.1:8899")
            print(f"  RakNet: 127.0.0.1:19132")
            
            # 测试假房间响应
            print("\n测试假房间响应:")
            room = proxy._build_fake_room_response()
            print(f"  Room ID: {room['roomid']}")
            print(f"  Room Name: {room['room_name']}")
            print(f"  IP: {room['ip']}:{room['port']}")
            
            # 统计
            stats = proxy.get_stats()
            print(f"\n统计: {stats}")
            
            print("\n按 Ctrl+C 停止...")
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n停止中...")
        finally:
            await proxy.stop()
            print("✓ 代理已停止")
    
    # 运行测试
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        pass
