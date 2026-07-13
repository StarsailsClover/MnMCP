"""
MnMCP v2.1 - 实用协议适配器
迷你世界 → Minecraft Bedrock (通过 Geyser)

使用方法:
1. 确保 Minecraft 服务器 + Geyser 已启动 (端口 19132)
2. 运行此脚本: python mnmcp_adapter.py
3. 迷你世界连接到: <IP>:19133
"""

import asyncio
import struct
import logging
from typing import Optional, Tuple
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MnWToBedrockAdapter:
    """迷你世界 → Bedrock 协议适配器"""
    
    def __init__(self, geyser_host: str = "127.0.0.1", geyser_port: int = 19132):
        self.geyser_host = geyser_host
        self.geyser_port = geyser_port
        self.server = None
        self.active_connections = 0
        
    async def start(self, listen_port: int = 19133):
        """启动适配器"""
        logger.info("=" * 60)
        logger.info("MnMCP v2.1 - 协议适配器")
        logger.info("=" * 60)
        
        # 检查 Geyser 是否可用
        if not await self.check_geyser():
            logger.error("✗ 无法连接到 Geyser")
            logger.error(f"  请确保 Minecraft 服务器 + Geyser 已启动")
            logger.error(f"  Geyser 应该监听: {self.geyser_host}:{self.geyser_port}")
            return
        
        # 启动服务器
        self.server = await asyncio.start_server(
            self.handle_mnw_client,
            '0.0.0.0',
            listen_port
        )
        
        logger.info("✓ MnMCP 适配器已启动")
        logger.info(f"  监听端口: {listen_port}")
        logger.info(f"  Geyser 地址: {self.geyser_host}:{self.geyser_port}")
        logger.info("=" * 60)
        logger.info("迷你世界玩家连接方式:")
        logger.info(f"  1. 打开迷你世界 1.55.0")
        logger.info(f"  2. 点击'联机' → '加入房间'")
        logger.info(f"  3. 输入地址: <服务器IP>:{listen_port}")
        logger.info(f"     局域网示例: 192.168.1.100:{listen_port}")
        logger.info(f"     本机测试: 127.0.0.1:{listen_port}")
        logger.info("=" * 60)
        
        async with self.server:
            await self.server.serve_forever()
    
    async def check_geyser(self) -> bool:
        """检查 Geyser 是否可用"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.geyser_host, self.geyser_port),
                timeout=2.0
            )
            writer.close()
            await writer.wait_closed()
            logger.info(f"✓ Geyser 连接正常: {self.geyser_host}:{self.geyser_port}")
            return True
        except Exception as e:
            logger.error(f"✗ Geyser 连接失败: {e}")
            return False
    
    async def handle_mnw_client(self, reader, writer):
        """处理迷你世界客户端连接"""
        addr = writer.get_extra_info('peername')
        self.active_connections += 1
        
        logger.info("=" * 60)
        logger.info(f"[连接 #{self.active_connections}] 迷你世界玩家: {addr[0]}:{addr[1]}")
        
        geyser_reader = None
        geyser_writer = None
        
        try:
            # 连接到 Geyser
            logger.info(f"[连接 #{self.active_connections}] 正在连接到 Geyser...")
            geyser_reader, geyser_writer = await asyncio.open_connection(
                self.geyser_host,
                self.geyser_port
            )
            
            logger.info(f"[连接 #{self.active_connections}] ✓ 已连接到 Geyser")
            logger.info(f"[连接 #{self.active_connections}] 开始数据转发...")
            
            # 双向转发
            await asyncio.gather(
                self.forward_mnw_to_bedrock(reader, geyser_writer, addr),
                self.forward_bedrock_to_mnw(geyser_reader, writer, addr),
                return_exceptions=True
            )
            
        except Exception as e:
            logger.error(f"[连接 #{self.active_connections}] 错误: {e}")
        finally:
            # 清理连接
            if geyser_writer:
                geyser_writer.close()
                await geyser_writer.wait_closed()
            
            writer.close()
            await writer.wait_closed()
            
            self.active_connections -= 1
            logger.info(f"[断开] {addr[0]}:{addr[1]} (剩余连接: {self.active_connections})")
            logger.info("=" * 60)
    
    async def forward_mnw_to_bedrock(self, mnw_reader, bedrock_writer, addr):
        """转发: 迷你世界 → Bedrock"""
        packet_count = 0
        
        while True:
            try:
                # 读取迷你世界数据包
                data = await mnw_reader.read(8192)
                if not data:
                    logger.info(f"[MNW→BE] {addr[0]} 连接关闭")
                    break
                
                packet_count += 1
                
                # 转换协议
                bedrock_packet = self.convert_mnw_to_bedrock(data)
                
                if bedrock_packet:
                    bedrock_writer.write(bedrock_packet)
                    await bedrock_writer.drain()
                    
                    if packet_count % 100 == 0:
                        logger.debug(f"[MNW→BE] {addr[0]} 已转发 {packet_count} 个数据包")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[MNW→BE] {addr[0]} 错误: {e}")
                break
    
    async def forward_bedrock_to_mnw(self, bedrock_reader, mnw_writer, addr):
        """转发: Bedrock → 迷你世界"""
        packet_count = 0
        
        while True:
            try:
                # 读取 Bedrock 数据包
                data = await bedrock_reader.read(8192)
                if not data:
                    logger.info(f"[BE→MNW] {addr[0]} 连接关闭")
                    break
                
                packet_count += 1
                
                # 转换协议
                mnw_packet = self.convert_bedrock_to_mnw(data)
                
                if mnw_packet:
                    mnw_writer.write(mnw_packet)
                    await mnw_writer.drain()
                    
                    if packet_count % 100 == 0:
                        logger.debug(f"[BE→MNW] {addr[0]} 已转发 {packet_count} 个数据包")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[BE→MNW] {addr[0]} 错误: {e}")
                break
    
    def convert_mnw_to_bedrock(self, mnw_data: bytes) -> Optional[bytes]:
        """转换: 迷你世界协议 → Bedrock 协议
        
        TODO: 实现完整的协议转换
        当前: 直接转发 (用于测试连接)
        """
        # 临时: 直接转发数据
        # 实际需要:
        # 1. 解析迷你世界数据包格式
        # 2. 提取游戏数据 (位置/方块/实体等)
        # 3. 转换为 Bedrock 数据包格式
        # 4. 应用方块/实体映射
        
        return mnw_data
    
    def convert_bedrock_to_mnw(self, bedrock_data: bytes) -> Optional[bytes]:
        """转换: Bedrock 协议 → 迷你世界协议
        
        TODO: 实现完整的协议转换
        当前: 直接转发 (用于测试连接)
        """
        # 临时: 直接转发数据
        # 实际需要:
        # 1. 解析 Bedrock 数据包格式
        # 2. 提取游戏数据
        # 3. 转换为迷你世界数据包格式
        # 4. 应用反向映射
        
        return bedrock_data


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MnMCP 协议适配器")
    parser.add_argument("--geyser-host", default="127.0.0.1", help="Geyser 主机地址")
    parser.add_argument("--geyser-port", type=int, default=19132, help="Geyser 端口")
    parser.add_argument("--listen-port", type=int, default=19133, help="监听端口")
    parser.add_argument("--debug", action="store_true", help="启用调试日志")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    adapter = MnWToBedrockAdapter(
        geyser_host=args.geyser_host,
        geyser_port=args.geyser_port
    )
    
    try:
        await adapter.start(listen_port=args.listen_port)
    except KeyboardInterrupt:
        logger.info("\n收到中断信号，正在停止...")
    except Exception as e:
        logger.error(f"运行错误: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")
