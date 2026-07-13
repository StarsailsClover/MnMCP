#!/usr/bin/env python3
"""
MnMCP v3 - 联机代理启动脚本
启动 MiniWorld <-> Minecraft JE 双向代理

架构:
  MiniWorld Client (RakNet:19132) -> ProxyServerV2 -> MC JE Server (TCP:25565)
                                                                      -> Geyser -> MC BE Client

使用方法:
  python run_proxy.py                      # 默认配置
  python run_proxy.py --mc-host 192.168.1.100  # 指定 MC 服务器
  python run_proxy.py --port 19133 --mc-port 25566  # 自定义端口
  python run_proxy.py --debug --log-packets  # 调试模式

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import asyncio
import argparse
import logging
import signal
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp_proxy.proxy_server import MnMCPProxyServer, ProxyServerConfig


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='MnMCP v3 - MiniWorld <-> Minecraft JE 联机代理',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_proxy.py                                    # 默认配置
  python run_proxy.py --mc-host 192.168.1.100            # 指定 MC 服务器
  python run_proxy.py --port 19133 --mc-port 25566       # 自定义端口
  python run_proxy.py --debug --log-packets --log-sync   # 详细调试
        """
    )
    
    # RakNet 配置
    parser.add_argument('--host', default='0.0.0.0',
                        help='RakNet 监听地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=19132,
                        help='RakNet 监听端口 (默认: 19132)')
    
    # MC 服务器配置
    parser.add_argument('--mc-host', default='127.0.0.1',
                        help='Minecraft JE 服务器地址 (默认: 127.0.0.1)')
    parser.add_argument('--mc-port', type=int, default=25565,
                        help='Minecraft JE 服务器端口 (默认: 25565)')
    parser.add_argument('--mc-protocol', type=int, default=766,
                        help='MC 协议版本 (默认: 766=1.20.6)')
    
    # 性能
    parser.add_argument('--max-clients', type=int, default=10,
                        help='最大客户端数 (默认: 10)')
    parser.add_argument('--sync-interval', type=float, default=0.05,
                        help='同步间隔秒 (默认: 0.05=20Hz)')
    
    # 调试
    parser.add_argument('--debug', action='store_true',
                        help='启用调试模式')
    parser.add_argument('--log-packets', action='store_true',
                        help='记录数据包日志')
    parser.add_argument('--log-sync', action='store_true',
                        help='记录同步日志')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='日志级别 (默认: INFO)')
    
    return parser.parse_args()


def setup_logging(args):
    """配置日志"""
    log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    date_format = '%H:%M:%S'
    
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format=log_format,
        datefmt=date_format
    )
    
    # 减少第三方库日志噪音
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)


async def main():
    """主函数"""
    args = parse_args()
    setup_logging(args)
    
    logger = logging.getLogger('MnMCP')
    
    print("=" * 60)
    print("  MnMCP v3 - MiniWorld <-> Minecraft JE 联机代理")
    print("  ProxyServerV2")
    print("=" * 60)
    print()
    
    # 创建配置
    config = ProxyServerConfig(
        raknet_host=args.host,
        raknet_port=args.port,
        mc_host=args.mc_host,
        mc_port=args.mc_port,
        mc_protocol=args.mc_protocol,
        max_clients=args.max_clients,
        sync_interval=args.sync_interval,
        debug=args.debug,
        log_packets=args.log_packets,
        log_sync=args.log_sync,
    )
    
    # 创建服务器
    server = MnMCPProxyServer(config)
    
    # 注册事件
    @server.on('started')
    async def on_started():
        print()
        print("=" * 60)
        print("  ProxyServerV2 已启动!")
        print(f"  MiniWorld 客户端请连接: {args.host}:{args.port}")
        print(f"  MC 服务器: {args.mc_host}:{args.mc_port}")
        print("=" * 60)
        print()
        print("等待 MiniWorld 客户端连接...")
        print("按 Ctrl+C 停止")
        print()
    
    @server.on('client_login')
    async def on_client_login(conn_id, session):
        logger.info(f"客户端登录: {session.mnw_name} [{conn_id}]")
    
    @server.on('client_enter_game')
    async def on_client_enter_game(conn_id, session):
        logger.info(f"客户端进入游戏: {session.mnw_name} -> MC:{session.mc_username}")
    
    @server.on('client_disconnect')
    async def on_client_disconnect(conn_id, reason):
        logger.info(f"客户端断开: {conn_id} ({reason})")
    
    @server.on('stopped')
    async def on_stopped():
        print()
        print("=" * 60)
        print("  ProxyServerV2 已停止")
        print("=" * 60)
    
    @server.on('error')
    async def on_error(e):
        logger.error(f"服务器错误: {e}")
    
    # 启动
    if not await server.start():
        logger.error("启动失败!")
        return 1
    
    # 运行统计输出
    async def stats_reporter():
        while server.is_running:
            await asyncio.sleep(30)
            stats = server.get_stats()
            sessions = server.get_active_sessions()
            
            if sessions:
                logger.info("--- 状态报告 ---")
                logger.info(f"活跃会话: {stats['sessions']}")
                for s in sessions:
                    logger.info(f"  {s['mnw_name']} -> MC:{s['mc_username']} "
                                f"pos={s['position']} "
                                f"MNW->MC:{s['packets_mnw_to_mc']} "
                                f"MC->MNW:{s['packets_mc_to_mnw']}")
                logger.info(f"总数据包: MNW->MC={stats['packets_mnw_to_mc']}, "
                            f"MC->MNW={stats['packets_mc_to_mnw']}")
                logger.info(f"聊天: {stats['chat_messages']}, "
                            f"位置同步: {stats['position_syncs']}")
    
    stats_task = asyncio.create_task(stats_reporter())
    
    # 等待停止信号
    try:
        # 保持运行
        while server.is_running:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print()
        logger.info("收到停止信号...")
    finally:
        stats_task.cancel()
        await server.stop()
    
    return 0


if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        pass