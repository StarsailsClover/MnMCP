#!/usr/bin/env python3
"""
Archive old files for Phase 8 cleanup
Moves redundant files to archive/
"""

import os
import shutil
from pathlib import Path

# Files to archive (redundant/old)
FILES_TO_ARCHIVE = [
    # Old development files
    "03-MnMCP-Protocol-Bridge",
    "09-MnMCP-DevResources",
    
    # Old documents (keep in git history, remove from working tree)
    "00_MN3_TAKEOVER_SUMMARY.md",
    "BEST_INTEGRATION_PLAN.md",
    "CODE_AUDIT_REPORT.md",
    "COMPLETION_REPORT.md",
    "DEVELOPMENT_SUMMARY.md",
    "FINAL_SUMMARY.md",
    "HANDOVER_DOCUMENT.md",
    "INTEGRATION_FINAL_REPORT.md",
    "INTEGRATION_IMPLEMENTATION.md",
    "INTEGRATION_PLAN.md",
    "INTEGRATION_PROGRESS_REPORT.md",
    "LAN_TEST_GUIDE.md",
    "LAN_TEST_READY.md",
    "MN2MC_COMPARISON_ANALYSIS.md",
    "MN3_DEVELOPMENT_START.md",
    "MN3_HANDOVER_REPORT.md",
    "MN3_REFACTOR_COMPLETE.md",
    "PHASE4_EXECUTION_PLAN.md",
    "PHASE4_EXECUTION_SUMMARY.md",
    "PHASE4_PROGRESS_REPORT.md",
    "PHASE5_EXECUTION_PLAN.md",
    "PHASE5_EXECUTION_SUMMARY.md",
    "PHASE6_COMPLETENESS_CHECK.md",
    "PHASE6_EXECUTION_PLAN.md",
    "PHASE6_EXECUTION_SUMMARY.md",
    "PHASE7_EXECUTION_PLAN.md",
    "PHASE7_PROGRESS_REPORT.md",
    "PROGRESS_UPDATE.md",
    "PROJECT_STRUCTURE.md",
    "QUICK_REFERENCE.md",
]

def archive_files():
    """Archive old files"""
    root = Path("C:/Users/Sails/Documents/Workspace/NormalWorkspace/Coding/MnMCP")
    archive_dir = root / "archive" / "phase8_cleanup"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    archived = []
    not_found = []
    
    for file_name in FILES_TO_ARCHIVE:
        src = root / file_name
        if src.exists():
            dst = archive_dir / file_name
            
            # Create parent directories
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file/directory
            if src.is_dir():
                shutil.move(str(src), str(dst))
            else:
                shutil.move(str(src), str(dst))
            
            archived.append(file_name)
            print(f"Archived: {file_name}")
        else:
            not_found.append(file_name)
    
    print(f"\nArchived: {len(archived)} items")
    print(f"Not found: {len(not_found)} items")
    
    if not_found:
        print("\nNot found (may already be archived):")
        for f in not_found:
            print(f"  - {f}")

if __name__ == "__main__":
    print("Phase 8: Archiving old files...")
    print("=" * 60)
    archive_files()
    print("\nDone. Files moved to archive/phase8_cleanup/")
