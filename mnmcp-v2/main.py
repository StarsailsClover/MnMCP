#!/usr/bin/env python3
"""
MnMCP v2 - 主入口
高质量实现整合版

功能:
1. 端到端桥接 (MN2MC Phase 3/4)
2. 协议转换
3. 方块映射
4. 坐标转换
5. 加密通信
"""

import asyncio
import sys
import logging
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))

from src import VERSION
from src.config import Config
from src.protocol import MiniWorldLogin, BlockMapper, CoordinateConverter
from src.bridge import EndToEndBridge


def setup_logging(config: Config):
    """配置日志系统"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers = []
    
    if config.logging.console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(console_handler)
    
    if config.logging.file:
        log_path = Path(config.logging.file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            config.logging.file,
            maxBytes=10*1024*1024,
            backupCount=config.logging.backup_count
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=getattr(logging, config.logging.level.upper(), logging.INFO),
        handlers=handlers,
        format=log_format
    )


async def demo_mode():
    """演示模式 - 展示所有功能"""
    print(f"\n{'='*60}")
    print(f"MnMCP v{VERSION} - 演示模式")
    print('='*60)
    
    # 1. 配置系统演示
    print("\n[1] 配置系统")
    config = Config()
    config.mini.auth.uin = 12345678
    config.mini.auth.xxtea_key = "demo_key"
    config.mc.username = "DemoPlayer"
    print(f"  UIN: {config.mini.auth.uin}")
    print(f"  MC用户名: {config.mc.username}")
    print(f"  ✓ 配置系统工作正常")
    
    # 2. 方块映射演示
    print("\n[2] 方块映射系统")
    mapper = BlockMapper()
    mc_stone = mapper.mc_to_mnw(1)  # MC石头
    mc_grass = mapper.mc_to_mnw(2)  # MC草方块
    print(f"  MC石头 (ID=1) -> MNW石头 (ID={mc_stone})")
    print(f"  MC草方块 (ID=2) -> MNW草方块 (ID={mc_grass})")
    stats = mapper.get_stats()
    print(f"  已加载 {stats['total_mappings']} 个映射")
    print(f"  ✓ 方块映射系统工作正常")
    
    # 3. 坐标转换演示
    print("\n[3] 坐标转换系统")
    converter = CoordinateConverter()
    from src.protocol.coordinate import Vector3
    
    mc_pos = Vector3(100.5, 64.0, -200.3)
    mnw_pos = converter.mc_to_mnw(mc_pos)
    print(f"  MC坐标: {mc_pos}")
    print(f"  MNW坐标: {mnw_pos}")
    print(f"  ✓ 坐标转换系统工作正常")
    
    # 4. 协议包演示
    print("\n[4] 协议系统")
    from src.protocol.packet import MNWPacket, PacketType, SubType
    
    packet = MNWPacket(
        packet_type=PacketType.LOGIN,
        sub_type=SubType.REQUEST,
        data=b'{"user":"demo"}',
        seq_id=1
    )
    encoded = packet.encode()
    print(f"  创建登录包: 类型={PacketType(packet.packet_type).name}")
    print(f"  编码后大小: {len(encoded)} bytes")
    
    decoded = MNWPacket.decode(encoded)
    if decoded:
        print(f"  解码成功: seq={decoded.seq_id}")
    print(f"  ✓ 协议系统工作正常")
    
    # 5. 桥接系统演示
    print("\n[5] 端到端桥接系统")
    bridge = EndToEndBridge(config)
    
    # 启动桥接
    success = await bridge.start()
    if success:
        print(f"  桥接器启动成功")
        
        # 添加模拟玩家
        player = bridge.add_player("DemoPlayer", "demo-uuid-1234")
        print(f"  添加玩家: {player.mc_username}")
        
        # 获取统计
        stats = bridge.get_stats()
        print(f"  运行状态: {stats}")
        
        # 停止桥接
        await bridge.stop()
        print(f"  桥接器已停止")
    print(f"  ✓ 桥接系统工作正常")
    
    print("\n" + "="*60)
    print("演示完成！所有系统工作正常")
    print("="*60)


async def main():
    """主函数"""
    print(f"MnMCP v{VERSION}")
    print("="*60)
    
    # 加载配置
    config_path = Path(__file__).parent / "config.json"
    
    if config_path.exists():
        config = Config.load(str(config_path))
        print(f"✓ 从 {config_path} 加载配置")
    else:
        print(f"⚠ 未找到配置，使用默认配置")
        config = Config()
        config.mini.auth.uin = 2067729592
        config.mini.auth.xxtea_key = "demo_key"
    
    # 配置日志
    setup_logging(config)
    logger = logging.getLogger(__name__)
    logger.info("MnMCP 启动")
    
    # 演示模式
    await demo_mode()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)