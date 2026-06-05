"""
MnMCP v3 - 桥接核心
实现 MC <-> MNW 双向桥接
"""

import asyncio
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
import logging

from ..mcp_mc.client import MCPMinecraftClient, MCClientConfig
from ..mcp_mini.client import MCPMiniClient, MiniClientConfig, MiniAuthConfig

logger = logging.getLogger(__name__)


class BridgeState(IntEnum):
    """桥接状态"""
    STOPPED = 0
    STARTING = 1
    CONNECTING = 2
    CONNECTED = 3
    BRIDGING = 4
    DISCONNECTING = 5
    ERROR = 6


@dataclass
class MCPBridgeConfig:
    """桥接配置"""
    # MC 服务器配置
    mc_host: str = "127.0.0.1"
    mc_port: int = 25565
    mc_username: str = "BridgePlayer"
    
    # MNW 认证配置
    mnw_uin: int = 0
    mnw_passwd: str = ""
    mnw_device_id: str = ""
    
    # MNW 代理配置 (可选)
    use_proxy: bool = False
    proxy_host: str = "127.0.0.1"
    proxy_http_port: int = 8899
    proxy_raknet_port: int = 19132
    
    # 同步设置
    sync_interval: float = 0.05  # 20Hz
    position_threshold: float = 0.1
    
    # 调试
    debug: bool = False
    log_packets: bool = False
    log_sync: bool = False


@dataclass
class BridgeStats:
    """桥接统计"""
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    
    # 连接状态
    mc_connected: bool = False
    mc_logged_in: bool = False
    mc_in_game: bool = False
    
    mnw_connected: bool = False
    mnw_logged_in: bool = False
    mnw_in_game: bool = False
    
    # 转发统计
    packets_mc_to_mnw: int = 0
    packets_mnw_to_mc: int = 0
    bytes_mc_to_mnw: int = 0
    bytes_mnw_to_mc: int = 0
    
    # 同步统计
    position_syncs: int = 0
    chat_messages: int = 0
    block_placements: int = 0
    block_destructions: int = 0


class MCPBridge:
    """
    MnMCP 桥接核心
    
    功能:
    - 管理 MC 和 MNW 客户端连接
    - 实现双向数据包转发
    - 同步玩家位置
    - 桥接聊天消息
    - 同步方块交互
    
    使用示例:
        config = MCPBridgeConfig(
            mc_host="localhost",
            mc_port=25565,
            mc_username="BridgePlayer",
            mnw_uin=123456,
            mnw_passwd="password"
        )
        
        bridge = MCPBridge(config)
        await bridge.start()
        
        # 桥接运行中...
        
        await bridge.stop()
    """
    
    def __init__(self, config: Optional[MCPBridgeConfig] = None):
        """
        初始化桥接器
        
        Args:
            config: 桥接配置
        """
        self.config = config or MCPBridgeConfig()
        self.stats = BridgeStats()
        
        # 状态
        self._state = BridgeState.STOPPED
        self._running = False
        
        # 客户端
        self.mc_client: Optional[MCPMinecraftClient] = None
        self.mnw_client: Optional[MCPMiniClient] = None
        
        # 同步任务
        self._sync_task: Optional[asyncio.Task] = None
        
        # 事件处理器
        self._event_handlers: Dict[str, List[Callable]] = {
            'started': [],
            'connected': [],
            'bridging': [],
            'disconnected': [],
            'stopped': [],
            'error': [],
        }
        
        # 最后同步的位置
        self._last_mc_pos: Optional[tuple] = None
        self._last_mnw_pos: Optional[tuple] = None
    
    @property
    def state(self) -> BridgeState:
        """当前桥接状态"""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running and self._state == BridgeState.BRIDGING
    
    async def start(self) -> bool:
        """
        启动桥接
        
        Returns:
            是否启动成功
        """
        try:
            self._state = BridgeState.STARTING
            logger.info("Starting bridge...")
            
            # 创建客户端
            if not await self._create_clients():
                return False
            
            # 注册事件处理器
            self._register_handlers()
            
            self._state = BridgeState.CONNECTING
            
            # 连接 MC
            if not await self._connect_mc():
                logger.error("Failed to connect MC")
                return False
            
            # 连接 MNW
            if not await self._connect_mnw():
                logger.error("Failed to connect MNW")
                return False
            
            self._state = BridgeState.CONNECTED
            logger.info("Both clients connected")
            
            # 启动同步循环
            self._running = True
            self._sync_task = asyncio.create_task(self._sync_loop())
            
            self._state = BridgeState.BRIDGING
            self.stats.started_at = datetime.now()
            
            logger.info("Bridge started successfully!")
            await self._trigger_event('bridging')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start bridge: {e}")
            self._state = BridgeState.ERROR
            await self._trigger_event('error', e)
            return False
    
    async def _create_clients(self) -> bool:
        """创建客户端实例"""
        try:
            # MC 客户端
            mc_config = MCClientConfig(
                host=self.config.mc_host,
                port=self.config.mc_port,
                username=self.config.mc_username,
                debug=self.config.debug
            )
            self.mc_client = MCPMinecraftClient(mc_config)
            
            # MNW 客户端
            mnw_auth = MiniAuthConfig(
                uin=self.config.mnw_uin,
                passwd=self.config.mnw_passwd,
                device_id=self.config.mnw_device_id
            )
            mnw_config = MiniClientConfig(
                auth=mnw_auth,
                debug=self.config.debug
            )
            self.mnw_client = MCPMiniClient(mnw_config)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create clients: {e}")
            return False
    
    def _register_handlers(self) -> None:
        """注册事件处理器"""
        if not self.mc_client or not self.mnw_client:
            return
        
        # MC 事件
        @self.mc_client.on('join')
        async def on_mc_join():
            self.stats.mc_in_game = True
            logger.info("MC player joined game")
        
        @self.mc_client.on('disconnect')
        async def on_mc_disconnect(reason):
            self.stats.mc_connected = False
            logger.info(f"MC disconnected: {reason}")
            if self._running:
                await self.stop()
        
        # MNW 事件
        @self.mnw_client.on('enter_world')
        async def on_mnw_enter():
            self.stats.mnw_in_game = True
            logger.info("MNW player entered world")
        
        @self.mnw_client.on('disconnect')
        async def on_mnw_disconnect(reason):
            self.stats.mnw_connected = False
            logger.info(f"MNW disconnected: {reason}")
            if self._running:
                await self.stop()
    
    async def _connect_mc(self) -> bool:
        """连接 MC"""
        if not self.mc_client:
            return False
        
        logger.info("Connecting to MC...")
        
        if not await self.mc_client.connect():
            return False
        
        self.stats.mc_connected = True
        
        # 登录
        # await self.mc_client.login()
        
        return True
    
    async def _connect_mnw(self) -> bool:
        """连接 MNW"""
        if not self.mnw_client:
            return False
        
        logger.info("Connecting to MNW...")
        
        # 登录
        if not await self.mnw_client.login():
            return False
        
        self.stats.mnw_connected = True
        
        # 获取房间列表
        rooms = await self.mnw_client.get_room_list()
        if not rooms:
            logger.error("No rooms available")
            return False
        
        # 加入第一个房间
        if not await self.mnw_client.join_room(rooms[0].room_id):
            return False
        
        return True
    
    async def _sync_loop(self) -> None:
        """同步循环"""
        logger.debug("Sync loop started")
        
        while self._running:
            try:
                # 同步位置
                await self._sync_position()
                
                # 其他同步
                # await self._sync_other()
                
                await asyncio.sleep(self.config.sync_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                await asyncio.sleep(0.1)
        
        logger.debug("Sync loop stopped")
    
    async def _sync_position(self) -> None:
        """同步位置"""
        if not self.mc_client or not self.mnw_client:
            return
        
        if not self.mc_client.is_in_game or not self.mnw_client.is_in_game:
            return
        
        # 获取 MC 位置
        mc_pos = self.mc_client.position
        mc_pos_tuple = (mc_pos.x, mc_pos.y, mc_pos.z, mc_pos.yaw, mc_pos.pitch)
        
        # 检查是否移动足够
        if self._last_mc_pos:
            dx = mc_pos_tuple[0] - self._last_mc_pos[0]
            dy = mc_pos_tuple[1] - self._last_mc_pos[1]
            dz = mc_pos_tuple[2] - self._last_mc_pos[2]
            dist_sq = dx*dx + dy*dy + dz*dz
            
            if dist_sq < self.config.position_threshold * self.config.position_threshold:
                return  # 移动太小，不同步
        
        # 更新最后位置
        self._last_mc_pos = mc_pos_tuple
        
        # 转换朝向
        mnw_yaw = self._mc_yaw_to_mnw(mc_pos.yaw)
        mnw_pitch = mc_pos.pitch
        
        # 发送到 MNW
        await self.mnw_client.send_move(
            mc_pos.x, mc_pos.y, mc_pos.z,
            mnw_yaw, mnw_pitch
        )
        
        self.stats.position_syncs += 1
        
        if self.config.log_sync:
            logger.debug(f"Position sync: ({mc_pos.x:.2f}, {mc_pos.y:.2f}, {mc_pos.z:.2f})")
    
    def _mc_yaw_to_mnw(self, mc_yaw: float) -> float:
        """MC Yaw -> MNW Yaw"""
        # MC: -180=北, -90=东, 0=南, 90=西, 180=北
        # MNW: 0=北, 90=东, 180=南, 270=西
        mnw_yaw = (mc_yaw + 180) % 360
        return mnw_yaw
    
    def _mnw_yaw_to_mc(self, mnw_yaw: float) -> float:
        """MNW Yaw -> MC Yaw"""
        mc_yaw = (mnw_yaw - 180) % 360
        if mc_yaw > 180:
            mc_yaw -= 360
        return mc_yaw
    
    async def send_chat(self, message: str, source: str = "bridge") -> None:
        """
        发送聊天消息到两端
        
        Args:
            message: 消息内容
            source: 来源标识
        """
        full_message = f"[{source}] {message}"
        
        if self.mc_client and self.mc_client.is_in_game:
            await self.mc_client.send_chat(full_message)
        
        if self.mnw_client and self.mnw_client.is_in_game:
            await self.mnw_client.send_chat(full_message)
        
        self.stats.chat_messages += 1
    
    async def stop(self, reason: str = "Bridge stop") -> None:
        """
        停止桥接
        
        Args:
            reason: 停止原因
        """
        if self._state == BridgeState.STOPPED:
            return
        
        logger.info(f"Stopping bridge: {reason}")
        self._state = BridgeState.DISCONNECTING
        
        self._running = False
        
        # 取消同步任务
        if self._sync_task and not self._sync_task.done():
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        
        # 断开客户端
        if self.mc_client:
            await self.mc_client.disconnect(reason)
            self.mc_client = None
        
        if self.mnw_client:
            await self.mnw_client.disconnect(reason)
            self.mnw_client = None
        
        self.stats.stopped_at = datetime.now()
        self._state = BridgeState.STOPPED
        
        logger.info("Bridge stopped")
        await self._trigger_event('stopped')
    
    def on(self, event: str) -> Callable:
        """
        注册事件处理器
        
        Args:
            event: 事件名
        """
        def decorator(func: Callable) -> Callable:
            if event not in self._event_handlers:
                self._event_handlers[event] = []
            self._event_handlers[event].append(func)
            return func
        return decorator
    
    async def _trigger_event(self, event: str, *args, **kwargs) -> None:
        """触发事件"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(*args, **kwargs)
                else:
                    handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in event handler for {event}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        runtime = None
        if self.stats.started_at:
            end_time = self.stats.stopped_at or datetime.now()
            runtime = (end_time - self.stats.started_at).total_seconds()
        
        return {
            'state': self._state.name,
            'running': self._running,
            'runtime': runtime,
            'mc_connected': self.stats.mc_connected,
            'mc_in_game': self.stats.mc_in_game,
            'mnw_connected': self.stats.mnw_connected,
            'mnw_in_game': self.stats.mnw_in_game,
            'packets_mc_to_mnw': self.stats.packets_mc_to_mnw,
            'packets_mnw_to_mc': self.stats.packets_mnw_to_mc,
            'position_syncs': self.stats.position_syncs,
            'chat_messages': self.stats.chat_messages,
        }


# 便捷函数
async def create_bridge(
    mc_host: str,
    mc_port: int,
    mc_username: str,
    mnw_uin: int,
    mnw_passwd: str
) -> MCPBridge:
    """
    快速创建桥接器
    
    Args:
        mc_host: MC 服务器地址
        mc_port: MC 端口
        mc_username: MC 用户名
        mnw_uin: MNW UIN
        mnw_passwd: MNW 密码
        
    Returns:
        桥接器实例
    """
    config = MCPBridgeConfig(
        mc_host=mc_host,
        mc_port=mc_port,
        mc_username=mc_username,
        mnw_uin=mnw_uin,
        mnw_passwd=mnw_passwd
    )
    return MCPBridge(config)


# 测试
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("MnMCP v3 - 桥接核心测试")
    print("=" * 60)
    
    async def test():
        # 创建桥接配置
        config = MCPBridgeConfig(
            mc_host="127.0.0.1",
            mc_port=25565,
            mc_username="BridgeTest",
            mnw_uin=123456,
            mnw_passwd="test_pass",
            debug=True
        )
        
        bridge = MCPBridge(config)
        
        # 注册事件
        @bridge.on('bridging')
        async def on_bridging():
            print("✓ 桥接开始!")
        
        @bridge.on('stopped')
        async def on_stopped():
            print("✓ 桥接停止!")
        
        @bridge.on('error')
        async def on_error(e):
            print(f"✗ 桥接错误: {e}")
        
        # 测试启动 (会失败，因为没有实际服务器)
        print("\n测试启动桥接...")
        started = await bridge.start()
        
        if started:
            print("✓ 桥接启动成功!")
            
            # 运行一段时间
            print("\n桥接运行中 (3秒)...")
            await asyncio.sleep(3)
            
            # 统计
            stats = bridge.get_stats()
            print(f"\n统计:")
            print(f"  状态: {stats['state']}")
            print(f"  MC 连接: {stats['mc_connected']}")
            print(f"  MNW 连接: {stats['mnw_connected']}")
            print(f"  位置同步: {stats['position_syncs']}")
            
            # 停止
            print("\n停止桥接...")
            await bridge.stop("Test complete")
        else:
            print("✗ 桥接启动失败 (预期，没有实际服务器)")
        
        print("\n✓ 桥接测试完成")
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(test())
    except KeyboardInterrupt:
        pass
