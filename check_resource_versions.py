#!/usr/bin/env python3
"""
MnMCP v3 - 资源版本检查器

检查所有资源文件的版本状态，判断是否需要更新

GitHub@StarsailsClover
©BlockConnect Team 2026
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

RESOURCES_DIR = Path(__file__).parent / "09-MnMCP-DevResources"
SRC_DIR = Path(__file__).parent / "src"


class ResourceChecker:
    """资源版本检查器"""
    
    def __init__(self):
        self.results: Dict[str, Dict] = {}
    
    def check_file_version(self, filepath: Path) -> Dict:
        """检查单个文件的版本信息"""
        if not filepath.exists():
            return {"exists": False, "version": "NOT_FOUND", "timestamp": None}
        
        timestamp = filepath.stat().st_mtime
        mtime = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        version = "UNKNOWN"
        size = filepath.stat().st_size
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2000)
                
                version_patterns = [
                    r'version\s*[:=]\s*["\']([^"\']+)["\']',
                    r'VERSION\s*=\s*["\']([^"\']+)["\']',
                    r'__version__\s*[:=]\s*["\']([^"\']+)["\']',
                    r'v\d+\.\d+\.\d+',
                ]
                
                for pattern in version_patterns:
                    match = re.search(pattern, content)
                    if match:
                        version = match.group(1)
                        break
        except:
            pass
        
        return {
            "exists": True,
            "version": version,
            "timestamp": mtime,
            "size": size,
            "path": str(filepath)
        }
    
    def check_csv_definitions(self) -> Dict:
        """检查CSV定义文件"""
        csv_dir = RESOURCES_DIR / "MnMCPResources" / "csvdef" / "utf8"
        if not csv_dir.exists():
            return {"status": "MISSING", "count": 0}
        
        csv_files = list(csv_dir.glob("*.csv"))
        key_files = [
            "blockdef.csv", "itemdef.csv", "material.csv", "monster.csv",
            "biomedef.csv", "enchant.csv", "recipe.csv", "skilldef.csv"
        ]
        
        results = {
            "status": "OK",
            "total_count": len(csv_files),
            "key_files": {}
        }
        
        for key_file in key_files:
            filepath = csv_dir / key_file
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    results["key_files"][key_file] = {
                        "exists": True,
                        "lines": len(lines),
                        "columns": len(lines[0].split(',')) if lines else 0
                    }
            else:
                results["key_files"][key_file] = {"exists": False}
        
        return results
    
    def check_so_files(self) -> Dict:
        """检查SO文件"""
        so_dir = RESOURCES_DIR / "MnMCPResources" / "packs_downloads" / "decompiled_official" / "lib" / "arm64-v8a"
        if not so_dir.exists():
            return {"status": "MISSING", "files": []}
        
        so_files = list(so_dir.glob("*.so*"))
        results = {
            "status": "OK" if so_files else "EMPTY",
            "count": len(so_files),
            "files": []
        }
        
        for so_file in so_files:
            info = self.check_file_version(so_file)
            info["filename"] = so_file.name
            results["files"].append(info)
        
        return results
    
    def check_protocol_docs(self) -> Dict:
        """检查协议文档"""
        docs = {
            "PROTOCOL_ANALYSIS.md": RESOURCES_DIR / "MnMCPResources" / "PROTOCOL_ANALYSIS.md",
            "PROTOCOL_IMPLEMENTATION_GUIDE.md": RESOURCES_DIR / "MnMCPResources" / "PROTOCOL_IMPLEMENTATION_GUIDE.md",
            "MEMORY_SIGNATURES_REPORT.md": RESOURCES_DIR / "MnMCPResources" / "MEMORY_SIGNATURES_REPORT.md",
        }
        
        results = {}
        for name, path in docs.items():
            results[name] = self.check_file_version(path)
        
        return results
    
    def check_core_code(self) -> Dict:
        """检查核心代码文件"""
        core_files = [
            ("bridge.py", SRC_DIR / "mcp_core" / "bridge.py"),
            ("xxtea_mcp.py", SRC_DIR / "mcp_crypto" / "xxtea_mcp.py"),
            ("auth_mcp.py", SRC_DIR / "mcp_crypto" / "auth_mcp.py"),
            ("client.py (MNW)", SRC_DIR / "mcp_mini" / "client.py"),
            ("client.py (MC)", SRC_DIR / "mcp_mc" / "client.py"),
            ("msgcode_registry.py", SRC_DIR / "mcp_protocol" / "msgcode_registry.py"),
            ("codec.py", SRC_DIR / "mcp_protocol" / "codec.py"),
            ("blocks_full.py", SRC_DIR / "mcp_mapping" / "blocks_full.py"),
            ("mcp_config.py", SRC_DIR / "mcp_config.py"),
        ]
        
        results = {}
        for name, path in core_files:
            results[name] = self.check_file_version(path)
        
        return results
    
    def check_mn2mc_reference(self) -> Dict:
        """检查MN2MC引用路径"""
        mn2mc_path = Path(r"C:\Users\Sails\Downloads\Official-MN2MC\MN2MC-main\mn2mc\mapping\blocks.py")
        
        return {
            "exists": mn2mc_path.exists(),
            "path": str(mn2mc_path),
            "timestamp": datetime.fromtimestamp(mn2mc_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S") if mn2mc_path.exists() else None
        }
    
    def check_env_config(self) -> Dict:
        """检查环境配置"""
        env_file = Path(__file__).parent / ".env"
        config_file = Path(__file__).parent / "config.yaml"
        
        env_vars = {}
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value[:4] + "***" if len(value) > 4 else value
        
        return {
            "env_file_exists": env_file.exists(),
            "config_file_exists": config_file.exists(),
            "env_vars": env_vars
        }
    
    def run_all_checks(self):
        """运行所有检查"""
        print("=" * 70)
        print("MnMCP v3 - 资源版本全面检查")
        print("=" * 70)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 70)
        
        print("\n[1] CSV定义文件检查")
        print("-" * 50)
        csv_result = self.check_csv_definitions()
        print(f"  状态: {csv_result['status']}")
        print(f"  总文件数: {csv_result['total_count']}")
        print("  关键文件:")
        for filename, info in csv_result["key_files"].items():
            if info["exists"]:
                status = f"✓ {info['lines']}行, {info['columns']}列"
            else:
                status = "✗ 缺失"
            print(f"    {filename:<25} {status}")
        
        print("\n[2] SO库文件检查 (arm64-v8a)")
        print("-" * 50)
        so_result = self.check_so_files()
        print(f"  状态: {so_result['status']}")
        print(f"  文件数: {so_result['count']}")
        for file_info in so_result["files"]:
            print(f"    {file_info['filename']:<30} {file_info['size']:,} bytes  ({file_info['timestamp']})")
        
        print("\n[3] 协议文档检查")
        print("-" * 50)
        doc_result = self.check_protocol_docs()
        for doc_name, info in doc_result.items():
            status = "✓" if info["exists"] else "✗"
            version = info["version"] if info["version"] != "UNKNOWN" else ""
            print(f"    {status} {doc_name:<45} {version}")
        
        print("\n[4] 核心代码检查")
        print("-" * 50)
        code_result = self.check_core_code()
        for name, info in code_result.items():
            status = "✓" if info["exists"] else "✗"
            version = info["version"] if info["version"] != "UNKNOWN" else ""
            print(f"    {status} {name:<35} {version}")
        
        print("\n[5] MN2MC引用检查")
        print("-" * 50)
        mn2mc_result = self.check_mn2mc_reference()
        status = "✓" if mn2mc_result["exists"] else "✗"
        print(f"    {status} MN2MC blocks.py")
        print(f"    路径: {mn2mc_result['path']}")
        if mn2mc_result["timestamp"]:
            print(f"    修改时间: {mn2mc_result['timestamp']}")
        
        print("\n[6] 环境配置检查")
        print("-" * 50)
        env_result = self.check_env_config()
        print(f"    .env 文件: {'✓' if env_result['env_file_exists'] else '✗'}")
        print(f"    config.yaml: {'✓' if env_result['config_file_exists'] else '✗'}")
        if env_result["env_vars"]:
            print("    环境变量:")
            for key, value in env_result["env_vars"].items():
                print(f"      {key} = {value}")
        
        print("\n" + "=" * 70)
        print("检查总结")
        print("=" * 70)
        self._generate_summary()
    
    def _generate_summary(self):
        """生成总结报告"""
        issues = []
        warnings = []
        
        csv_result = self.check_csv_definitions()
        if csv_result["status"] == "MISSING":
            issues.append("CSV定义目录不存在")
        
        so_result = self.check_so_files()
        if so_result["count"] == 0:
            warnings.append("SO库文件目录为空")
        elif so_result["count"] < 5:
            warnings.append(f"SO库文件较少 ({so_result['count']}个)")
        
        doc_result = self.check_protocol_docs()
        missing_docs = [name for name, info in doc_result.items() if not info["exists"]]
        if missing_docs:
            issues.append(f"协议文档缺失: {', '.join(missing_docs)}")
        
        code_result = self.check_core_code()
        missing_code = [name for name, info in code_result.items() if not info["exists"]]
        if missing_code:
            issues.append(f"核心代码缺失: {', '.join(missing_code)}")
        
        mn2mc_result = self.check_mn2mc_reference()
        if not mn2mc_result["exists"]:
            warnings.append("MN2MC引用路径不存在 (extract_mappings.py需要)")
        
        env_result = self.check_env_config()
        if not env_result["env_file_exists"]:
            warnings.append(".env 文件不存在")
        
        print(f"\n问题列表 ({len(issues)}):")
        if issues:
            for i, issue in enumerate(issues, 1):
                print(f"  [{i}] ✗ {issue}")
        else:
            print("  无")
        
        print(f"\n警告列表 ({len(warnings)}):")
        if warnings:
            for i, warning in enumerate(warnings, 1):
                print(f"  [{i}] ⚠️ {warning}")
        else:
            print("  无")
        
        print("\n资源状态评估:")
        if issues:
            print("  状态: 需要修复问题后才能启动开发")
        elif warnings:
            print("  状态: 基本就绪，但有一些警告需要注意")
        else:
            print("  状态: 所有资源就绪，可以启动开发")


if __name__ == "__main__":
    checker = ResourceChecker()
    checker.run_all_checks()