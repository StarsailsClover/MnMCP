#!/usr/bin/env python3
"""
MnMCP 启动脚本 (修正版)
正确的架构：本地代理 + Java中转服务器
"""

import sys
import asyncio
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def print_banner():
    print("=" * 60)
    print(" MnMCP - Minecraft & MiniWorld Cross-Platform")
    print(" 修正版架构 - 本地代理 + Java中转")
    print("=" * 60)
    print()

def check_components():
    """检查必要组件"""
    print("[1/3] 检查组件...")
    
    # 检查代理服务器
    proxy_path = Path("src/core/local_proxy.py")
    if proxy_path.exists():
        print("  [OK] 代理服务器模块")
    else:
        print("  [ERROR] 代理服务器模块缺失")
        return False
    
    # 检查协议翻译
    translator_path = Path("src/protocol/packet_translator.py")
    if translator_path.exists():
        print("  [OK] 协议翻译模块")
    else:
        print("  [ERROR] 协议翻译模块缺失")
        return False
    
    # 检查方块映射
    mapping_path = Path("data/mnw_block_mapping_from_go.json")
    if mapping_path.exists():
        print("  [OK] 方块映射数据")
    else:
        print("  [ERROR] 方块映射数据缺失")
        return False
    
    return True

def show_menu():
    """显示菜单"""
    print()
    print("选择操作:")
    print("[1] 启动本地代理服务器")
    print("[2] 配置系统代理")
    print("[3] 运行功能演示")
    print("[4] 检查项目完整性")
    print("[5] 查看使用说明")
    print("[6] 退出")
    print()
    return input("请输入选项 (1-6): ").strip()

def start_proxy():
    """启动代理服务器"""
    print()
    print("[2/3] 启动本地代理服务器...")
    print()
    print("架构说明:")
    print("  迷你世界客户端 → 本地代理(19132) → Java服务器(25565)")
    print()
    print("请先确保:")
    print("  1. Java服务器(PaperMC)已启动在 127.0.0.1:25565")
    print("  2. 已配置系统代理指向 127.0.0.1:19132")
    print()
    
    confirm = input("确认启动? (y/n): ").strip().lower()
    if confirm != 'y':
        return
    
    try:
        from core.local_proxy import MiniWorldLocalProxy
        
        proxy = MiniWorldLocalProxy(
            local_host="127.0.0.1",
            local_port=19132,
            mc_host="127.0.0.1",
            mc_port=25565
        )
        
        print()
        print("代理服务器启动中...")
        print("按 Ctrl+C 停止")
        print()
        
        asyncio.run(proxy.start())
        
    except KeyboardInterrupt:
        print("\n[OK] 代理服务器已停止")
    except Exception as e:
        print(f"\n[ERROR] 启动失败: {e}")

def configure_proxy():
    """配置系统代理"""
    print()
    print("[3/3] 配置系统代理...")
    print()
    
    import subprocess
    subprocess.run([sys.executable, "tools/configure_proxy.py"])

def run_demo():
    """运行演示"""
    print()
    print("运行功能演示...")
    print()
    
    import subprocess
    subprocess.run([sys.executable, "demo_connection.py"])

def check_integrity():
    """检查完整性"""
    print()
    print("检查项目完整性...")
    print()
    
    import subprocess
    subprocess.run([sys.executable, "check_project_integrity.py"])

def show_guide():
    """显示使用说明"""
    print()
    print("=" * 60)
    print("MnMCP 使用说明")
    print("=" * 60)
    print()
    print("正确联机流程:")
    print()
    print("1. 启动Java服务器")
    print("   cd server/paper")
    print("   java -jar paper-1.20.6.jar")
    print()
    print("2. 配置系统代理")
    print("   python tools/configure_proxy.py")
    print("   选择 [1] Enable system proxy")
    print()
    print("3. 启动MnMCP代理")
    print("   python start.py")
    print("   选择 [1] 启动本地代理服务器")
    print()
    print("4. 启动迷你世界")
    print("   正常启动游戏，流量将被代理拦截")
    print()
    print("5. Minecraft连接")
    print("   Java版: 连接 127.0.0.1:25565")
    print("   基岩版: 连接 127.0.0.1:19132")
    print()
    print("=" * 60)
    print()
    input("按 Enter 继续...")

def main():
    parser = argparse.ArgumentParser(description="MnMCP启动脚本")
    parser.add_argument("--proxy", action="store_true", help="直接启动代理服务器")
    parser.add_argument("--demo", action="store_true", help="运行演示")
    parser.add_argument("--check", action="store_true", help="检查完整性")
    args = parser.parse_args()
    
    if args.proxy:
        start_proxy()
        return
    
    if args.demo:
        run_demo()
        return
    
    if args.check:
        check_integrity()
        return
    
    # 正常启动流程
    print_banner()
    
    if not check_components():
        print()
        print("[ERROR] 组件检查失败，请检查项目完整性")
        return 1
    
    print()
    print("[OK] 组件检查通过")
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            start_proxy()
        elif choice == "2":
            configure_proxy()
        elif choice == "3":
            run_demo()
        elif choice == "4":
            check_integrity()
        elif choice == "5":
            show_guide()
        elif choice == "6":
            print()
            print("感谢使用 MnMCP!")
            break
        else:
            print("[ERROR] 无效选项")
        
        print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
