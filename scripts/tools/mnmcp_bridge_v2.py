"""
MnMCP v2.0 - Clash Meta 代理架构
基于迷你世界 P2P + 内网穿透机制的联机实现

架构说明:
1. 使用 Clash Meta 作为代理层
2. 模拟迷你世界房间（本地服务端）
3. 通过代理转发到 Minecraft Java 服务器
4. 支持方块/实体/物品映射
"""

import asyncio
import json
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:
    """代理配置"""
    clash_meta_port: int = 7890  # Clash Meta 代理端口
    clash_meta_api: str = "http://127.0.0.1:9090"  # Clash Meta API
    
    # 迷你世界配置
    mnw_local_port: int = 19132  # 本地模拟服务端端口
    mnw_room_name: str = "MnMCP Bridge Room"
    
    # Minecraft 配置
    mc_host: str = "127.0.0.1"
    mc_port: int = 25565
    mc_version: str = "1.20.6"  # 目标版本
    
    # 映射文件路径
    block_mapping_file: str = "data/block_mapping_v3_complete.json"
    entity_mapping_file: str = "data/entity_mapping_v1_complete.json"
    item_mapping_file: str = "data/item_mapping_v1_complete.json"


class MappingManager:
    """映射管理器 - 加载和管理方块/实体/物品映射"""
    
    def __init__(self, config: ProxyConfig):
        self.config = config
        self.block_mappings: Dict = {}
        self.entity_mappings: Dict = {}
        self.item_mappings: Dict = {}
        
        # 反向映射（MC -> MNW）
        self.block_mappings_reverse: Dict = {}
        self.entity_mappings_reverse: Dict = {}
        
    def load_mappings(self) -> bool:
        """加载所有映射文件"""
        try:
            # 加载方块映射
            logger.info("加载方块映射...")
            with open(self.config.block_mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.block_mappings = {
                    m['mnw_id']: m for m in data.get('mappings', [])
                }
                # 创建反向映射
                self.block_mappings_reverse = {
                    m['mc_registry']: m for m in data.get('mappings', [])
                    if 'mc_registry' in m
                }
            logger.info(f"✓ 加载了 {len(self.block_mappings)} 个方块映射")
            
            # 加载实体映射
            logger.info("加载实体映射...")
            with open(self.config.entity_mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.entity_mappings = {
                    m['mnw_id']: m for m in data.get('mappings', [])
                }
                self.entity_mappings_reverse = {
                    m['mc_entity']: m for m in data.get('mappings', [])
                    if 'mc_entity' in m
                }
            logger.info(f"✓ 加载了 {len(self.entity_mappings)} 个实体映射")
            
            # 加载物品映射
            logger.info("加载物品映射...")
            with open(self.config.item_mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.item_mappings = {
                    m['mnw_id']: m for m in data.get('mappings', [])
                }
            logger.info(f"✓ 加载了 {len(self.item_mappings)} 个物品映射")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ 加载映射文件失败: {e}")
            return False
    
    def mnw_block_to_mc(self, mnw_id: int) -> Optional[str]:
        """迷你世界方块 ID -> Minecraft 方块注册名"""
        mapping = self.block_mappings.get(mnw_id)
        if mapping:
            return mapping.get('mc_registry')
        return None
    
    def mc_block_to_mnw(self, mc_registry: str) -> Optional[int]:
        """Minecraft 方块注册名 -> 迷你世界方块 ID"""
        mapping = self.block_mappings_reverse.get(mc_registry)
        if mapping:
            return mapping.get('mnw_id')
        return None
    
    def mnw_entity_to_mc(self, mnw_id: int) -> Optional[str]:
        """迷你世界实体 ID -> Minecraft 实体"""
        mapping = self.entity_mappings.get(mnw_id)
        if mapping:
            return mapping.get('mc_entity')
        return None
    
    def mc_entity_to_mnw(self, mc_entity: str) -> Optional[int]:
        """Minecraft 实体 -> 迷你世界实体 ID"""
        mapping = self.entity_mappings_reverse.get(mc_entity)
        if mapping:
            return mapping.get('mnw_id')
        return None


class MiniWorldRoomSimulator:
    """迷你世界房间模拟器
    
    模拟迷你世界的本地服务端，接收迷你世界客户端的连接
    """
    
    def __init__(self, config: ProxyConfig, mapping_mgr: MappingManager):
        self.config = config
        self.mapping_mgr = mapping_mgr
        self.server = None
        self.clients = []
        self.running = False
        
    async def start(self) -> bool:
        """启动模拟服务端"""
        try:
            logger.info(f"启动迷你世界房间模拟器 (端口: {self.config.mnw_local_port})...")
            
            # 创建 UDP 服务器（迷你世界使用 UDP）
            self.server = await asyncio.start_server(
                self.handle_client,
                '0.0.0.0',
                self.config.mnw_local_port
            )
            
            self.running = True
            logger.info(f"✓ 房间模拟器已启动: {self.config.mnw_room_name}")
            logger.info(f"  监听地址: 0.0.0.0:{self.config.mnw_local_port}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ 启动房间模拟器失败: {e}")
            return False
    
    async def handle_client(self, reader, writer):
        """处理客户端连接"""
        addr = writer.get_extra_info('peername')
        logger.info(f"新客户端连接: {addr}")
        
        self.clients.append((reader, writer))
        
        try:
            while self.running:
                # 读取数据
                data = await reader.read(4096)
                if not data:
                    break
                
                # 处理数据包
                await self.process_packet(data, writer)
                
        except Exception as e:
            logger.error(f"处理客户端 {addr} 时出错: {e}")
        finally:
            logger.info(f"客户端断开: {addr}")
            self.clients.remove((reader, writer))
            writer.close()
            await writer.wait_closed()
    
    async def process_packet(self, data: bytes, writer):
        """处理数据包"""
        # TODO: 解析迷你世界协议包
        # TODO: 转换为 Minecraft 协议
        # TODO: 通过代理转发
        pass
    
    async def stop(self):
        """停止模拟服务端"""
        logger.info("停止房间模拟器...")
        self.running = False
        
        # 关闭所有客户端连接
        for reader, writer in self.clients:
            writer.close()
            await writer.wait_closed()
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        logger.info("✓ 房间模拟器已停止")


class ClashMetaProxy:
    """Clash Meta 代理管理器"""
    
    def __init__(self, config: ProxyConfig):
        self.config = config
        self.session = None
        
    async def check_status(self) -> bool:
        """检查 Clash Meta 状态"""
        try:
            import urllib.request
            import urllib.error
            
            req = urllib.request.Request(f"{self.config.clash_meta_api}/version")
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    logger.info(f"✓ Clash Meta 已连接: {data.get('version', 'unknown')}")
                    return True
        except Exception as e:
            logger.warning(f"⚠ Clash Meta 未运行，将使用直连模式")
            return False
    
    async def configure_rules(self):
        """配置代理规则"""
        # TODO: 配置 Clash Meta 规则
        # 将迷你世界流量路由到 Minecraft 服务器
        pass


class MinecraftConnector:
    """Minecraft 服务器连接器"""
    
    def __init__(self, config: ProxyConfig, mapping_mgr: MappingManager):
        self.config = config
        self.mapping_mgr = mapping_mgr
        self.reader = None
        self.writer = None
        self.connected = False
        
    async def connect(self) -> bool:
        """连接到 Minecraft 服务器"""
        try:
            logger.info(f"连接到 Minecraft 服务器 {self.config.mc_host}:{self.config.mc_port}...")
            
            self.reader, self.writer = await asyncio.open_connection(
                self.config.mc_host,
                self.config.mc_port
            )
            
            self.connected = True
            logger.info("✓ 已连接到 Minecraft 服务器")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ 连接 Minecraft 服务器失败: {e}")
            return False
    
    async def send_packet(self, packet: bytes):
        """发送数据包到 Minecraft 服务器"""
        if not self.connected:
            logger.error("未连接到 Minecraft 服务器")
            return
        
        try:
            self.writer.write(packet)
            await self.writer.drain()
        except Exception as e:
            logger.error(f"发送数据包失败: {e}")
    
    async def receive_packet(self) -> Optional[bytes]:
        """接收 Minecraft 服务器的数据包"""
        if not self.connected:
            return None
        
        try:
            data = await self.reader.read(4096)
            return data if data else None
        except Exception as e:
            logger.error(f"接收数据包失败: {e}")
            return None
    
    async def disconnect(self):
        """断开连接"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.connected = False
        logger.info("✓ 已断开 Minecraft 服务器连接")


class MnMCPBridge:
    """MnMCP 桥接器主类
    
    协调所有组件，实现迷你世界 ↔ Minecraft 联机
    """
    
    def __init__(self, config: ProxyConfig):
        self.config = config
        
        # 初始化组件
        self.mapping_mgr = MappingManager(config)
        self.room_simulator = MiniWorldRoomSimulator(config, self.mapping_mgr)
        self.clash_proxy = ClashMetaProxy(config)
        self.mc_connector = MinecraftConnector(config, self.mapping_mgr)
        
        self.running = False
        
    async def start(self) -> bool:
        """启动桥接器"""
        logger.info("=" * 60)
        logger.info("MnMCP v2.0 - Minecraft ↔ MiniWorld 联机桥接器")
        logger.info("=" * 60)
        
        # 1. 加载映射文件
        if not self.mapping_mgr.load_mappings():
            logger.error("✗ 加载映射文件失败，无法启动")
            return False
        
        # 2. 检查 Clash Meta
        if not await self.clash_proxy.check_status():
            logger.warning("⚠ Clash Meta 未运行，将使用直连模式")
        
        # 3. 连接 Minecraft 服务器
        if not await self.mc_connector.connect():
            logger.error("✗ 连接 Minecraft 服务器失败")
            return False
        
        # 4. 启动房间模拟器
        if not await self.room_simulator.start():
            logger.error("✗ 启动房间模拟器失败")
            await self.mc_connector.disconnect()
            return False
        
        self.running = True
        logger.info("=" * 60)
        logger.info("✓ 桥接器已启动！")
        logger.info("=" * 60)
        logger.info(f"迷你世界玩家可以连接到: 127.0.0.1:{self.config.mnw_local_port}")
        logger.info(f"房间名称: {self.config.mnw_room_name}")
        logger.info("=" * 60)
        
        # 5. 启动数据转发循环
        await self.run_bridge_loop()
        
        return True
    
    async def run_bridge_loop(self):
        """运行桥接循环"""
        logger.info("开始数据转发...")
        
        try:
            while self.running:
                # TODO: 实现双向数据转发
                # 1. 从迷你世界客户端接收数据
                # 2. 转换协议和映射
                # 3. 发送到 Minecraft 服务器
                # 4. 从 Minecraft 接收数据
                # 5. 转换并发送回迷你世界客户端
                
                await asyncio.sleep(0.01)  # 100Hz 更新频率
                
        except KeyboardInterrupt:
            logger.info("收到中断信号...")
        except Exception as e:
            logger.error(f"桥接循环出错: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """停止桥接器"""
        logger.info("停止桥接器...")
        self.running = False
        
        await self.room_simulator.stop()
        await self.mc_connector.disconnect()
        
        logger.info("✓ 桥接器已停止")


async def main():
    """主函数"""
    # 创建配置
    config = ProxyConfig(
        mc_host="127.0.0.1",
        mc_port=25565,
        mc_version="1.20.6",
        mnw_room_name="MnMCP Test Room"
    )
    
    # 创建并启动桥接器
    bridge = MnMCPBridge(config)
    await bridge.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序已退出")
