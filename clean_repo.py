#!/usr/bin/env python3
"""
Clean repository for open source
Remove cached files and dev resources from Git
"""

import subprocess
import sys
from pathlib import Path

def run_git(args):
    """Run git command"""
    cmd = ["git"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="C:/Users/Sails/Documents/Workspace/NormalWorkspace/Coding/MnMCP")
    return result

def remove_cached_files():
    """Remove __pycache__ and .pyc files from Git"""
    print("Removing Python cache files from Git...")
    
    # Find and remove __pycache__ directories
    result = run_git(["ls-files", "*__pycache__*"])
    if result.stdout:
        files = result.stdout.strip().split("\n")
        print(f"Found {len(files)} cache files")
        
        for f in files:
            if f:
                run_git(["rm", "--cached", "-r", f])
                print(f"  Removed: {f}")
    
    # Find and remove .pyc files
    result = run_git(["ls-files", "*.pyc"])
    if result.stdout:
        files = result.stdout.strip().split("\n")
        print(f"Found {len(files)} .pyc files")
        
        for f in files:
            if f:
                run_git(["rm", "--cached", f])
                print(f"  Removed: {f}")

def remove_dev_resources():
    """Remove dev resources from Git"""
    print("\nRemoving dev resources from Git...")
    
    dirs_to_remove = [
        "09-MnMCP-DevResources",
        "03-MnMCP-Protocol-Bridge",
    ]
    
    for d in dirs_to_remove:
        result = run_git(["ls-files", f"{d}/"])
        if result.stdout:
            files = result.stdout.strip().split("\n")
            print(f"Found {len(files)} files in {d}")
            
            for f in files:
                if f:
                    run_git(["rm", "--cached", f])
            print(f"  Removed: {d}/")

def remove_old_docs():
    """Remove old version docs from Git"""
    print("\nRemoving old version docs from Git...")
    
    patterns = [
        "PHASE*.md",
        "00_MN3_*.md",
        "BEST_*.md",
        "CODE_*.md",
        "COMPLETION_*.md",
        "DEVELOPMENT_*.md",
        "FINAL_*.md",
        "HANDOVER_*.md",
        "INTEGRATION_*.md",
        "LAN_TEST_*.md",
        "MN2MC_*.md",
        "MN3_*.md",
        "PROGRESS_*.md",
        "PROJECT_STRUCTURE.md",
        "QUICK_REFERENCE.md",
    ]
    
    for pattern in patterns:
        result = run_git(["ls-files", pattern])
        if result.stdout:
            files = result.stdout.strip().split("\n")
            
            for f in files:
                if f:
                    run_git(["rm", "--cached", f])
                    print(f"  Removed: {f}")

def main():
    print("=" * 60)
    print("Cleaning repository for open source")
    print("=" * 60)
    
    remove_cached_files()
    remove_dev_resources()
    remove_old_docs()
    
    print("\n" + "=" * 60)
    print("Done. Staged files for removal.")
    print("Run: git commit -m 'Remove non-essential files'")
    print("=" * 60)

if __name__ == "__main__":
    main()
