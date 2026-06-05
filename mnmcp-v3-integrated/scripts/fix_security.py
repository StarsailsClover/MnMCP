#!/usr/bin/env python3
"""
MnMCP v3 - 安全修复脚本
修复代码审计中发现的硬编码安全问题
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def find_security_issues(root_dir: str = "..") -> List[Tuple[str, int, str, str]]:
    """
    扫描安全问题
    
    返回: [(文件路径, 行号, 问题类型, 问题内容)]
    """
    issues = []
    root = Path(root_dir).resolve()
    
    # 扫描的文件模式
    patterns = {
        r'116\.205\.254\.\d+': '硬编码IP地址',
        r'["\']miniworld["\']': '硬编码认证字符串',
        r'19921|19601|14130|20000': '硬编码端口',
        r'hashlib\.md5\([^)]*["\']': 'MD5硬编码',
    }
    
    # 排除的目录
    exclude_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.venv'}
    
    for py_file in root.rglob('*.py'):
        # 跳过排除目录
        if any(excl in str(py_file) for excl in exclude_dirs):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                for pattern, issue_type in patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        # 排除注释行
                        stripped = line.strip()
                        if stripped.startswith('#'):
                            continue
                        
                        issues.append((
                            str(py_file.relative_to(root)),
                            line_num,
                            issue_type,
                            stripped[:80]
                        ))
        except Exception as e:
            print(f"⚠ 无法读取文件 {py_file}: {e}")
    
    return issues


def print_security_report(issues: List[Tuple[str, int, str, str]]):
    """打印安全报告"""
    print("=" * 80)
    print(" MnMCP v3 - 安全审计报告 ".center(80))
    print("=" * 80)
    
    if not issues:
        print("\n✓ 未发现安全问题\n")
        return
    
    print(f"\n发现 {len(issues)} 个安全问题:\n")
    
    # 按类型分组
    by_type = {}
    for file, line, issue_type, content in issues:
        if issue_type not in by_type:
            by_type[issue_type] = []
        by_type[issue_type].append((file, line, content))
    
    for issue_type, items in by_type.items():
        print(f"\n🔴 {issue_type} ({len(items)} 处)")
        print("-" * 80)
        for file, line, content in items:
            print(f"  {file}:{line}")
            print(f"    {content}")
    
    print("\n" + "=" * 80)
    print("\n修复建议:")
    print("  1. 将所有硬编码值移至环境变量或配置文件")
    print("  2. 使用 src/mcp_config.py 中的 MCPUnifiedConfig")
    print("  3. 运行 setup_environment() 设置环境变量")
    print("=" * 80)


def create_env_template():
    """创建环境变量模板文件"""
    template = """# MnMCP v3 - 环境变量配置
# 复制此文件为 .env 并填写实际值
# 永远不要将 .env 提交到 Git！

# MiniWorld 认证
MCP_MD5_SALT=your_md5_salt_here
MCP_DEVICE_ID=your_device_id_here

# 加密密钥 (必须16字节)
MCP_XXTEA_KEY=your_16byte_key_

# 可选: 自定义服务器地址
MCP_AUTH_HOST=wskacchm.mini1.cn
MCP_AUTH_PORT=14130
"""
    
    env_path = Path("../.env.template")
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"✓ 已创建环境变量模板: {env_path}")
    print("  请复制为 .env 并填写实际值")


def check_gitignore():
    """检查 .gitignore 是否包含敏感文件"""
    gitignore_path = Path("../.gitignore")
    
    required_patterns = [
        '.env',
        '*.env',
        'config.yaml',
        '*.log',
        '__pycache__/',
        '.pytest_cache/',
        '.coverage',
    ]
    
    existing = set()
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            existing = set(line.strip() for line in f)
    
    missing = [p for p in required_patterns if p not in existing]
    
    if missing:
        print("\n⚠ .gitignore 缺少以下安全规则:")
        for pattern in missing:
            print(f"  - {pattern}")
        
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write("\n# Security - Sensitive files\n")
            for pattern in missing:
                f.write(f"{pattern}\n")
        
        print("✓ 已自动添加到 .gitignore")
    else:
        print("✓ .gitignore 安全规则完整")


def main():
    """主函数"""
    print("=" * 80)
    print(" MnMCP v3 - 安全修复工具 ".center(80))
    print("=" * 80)
    
    # 1. 扫描安全问题
    print("\n🔍 扫描安全问题...")
    issues = find_security_issues()
    print_security_report(issues)
    
    # 2. 创建环境变量模板
    print("\n📄 创建环境变量模板...")
    create_env_template()
    
    # 3. 检查 .gitignore
    print("\n🔒 检查 Git 安全规则...")
    check_gitignore()
    
    # 4. 输出修复指南
    print("\n" + "=" * 80)
    print(" 安全修复指南 ".center(80))
    print("=" * 80)
    print("""
1. 设置环境变量 (Windows PowerShell):
   $env:MCP_MD5_SALT="your_actual_salt"
   $env:MCP_DEVICE_ID="your_device_id"
   $env:MCP_XXTEA_KEY="your_16byte_key"

2. 或使用 .env 文件:
   复制 .env.template 为 .env
   填写实际值
   
3. 使用新配置系统:
   from src.mcp_config import MCPUnifiedConfig, get_config
   
   config = get_config()  # 从环境变量加载
   print(config.auth.md5_salt)  # 安全读取

4. 验证修复:
   python scripts/fix_security.py
   应该显示: ✓ 未发现安全问题
""")
    
    print("=" * 80)
    
    if issues:
        return 1  # 发现安全问题
    return 0


if __name__ == "__main__":
    exit(main())
