#!/bin/bash
# Clean git repository - remove non-essential files from tracking

# Remove old docs from git (keep local)
git rm --cached -f PHASE*.md 2>/dev/null || true
git rm --cached -f 00_MN3_*.md 2>/dev/null || true
git rm --cached -f BEST_*.md 2>/dev/null || true
git rm --cached -f CODE_*.md 2>/dev/null || true
git rm --cached -f COMPLETION_*.md 2>/dev/null || true
git rm --cached -f DEVELOPMENT_*.md 2>/dev/null || true
git rm --cached -f FINAL_*.md 2>/dev/null || true
git rm --cached -f HANDOVER_*.md 2>/dev/null || true
git rm --cached -f INTEGRATION_*.md 2>/dev/null || true
git rm --cached -f LAN_TEST_*.md 2>/dev/null || true
git rm --cached -f MN2MC_*.md 2>/dev/null || true
git rm --cached -f MN3_*.md 2>/dev/null || true
git rm --cached -f PROGRESS_*.md 2>/dev/null || true
git rm --cached -f PROJECT_STRUCTURE.md 2>/dev/null || true
git rm --cached -f QUICK_REFERENCE.md 2>/dev/null || true
git rm --cached -f WORKSPACE_*.md 2>/dev/null || true
git rm --cached -f BLOCK_ID_TOOLS_README.md 2>/dev/null || true
git rm --cached -f DEPLOYMENT_GUIDE.md 2>/dev/null || true
git rm --cached -f TEST_*.md 2>/dev/null || true

# Remove scripts (except essentials)
git rm --cached -rf scripts/ 2>/dev/null || true

# Remove dev resources
git rm --cached -rf 09-MnMCP-DevResources/ 2>/dev/null || true
git rm --cached -rf 03-MnMCP-Protocol-Bridge/ 2>/dev/null || true
git rm --cached -rf MnMCP-Protocol/ 2>/dev/null || true
git rm --cached -rf archive/ 2>/dev/null || true

# Remove old versions
git rm --cached -rf mnmcp-v2/ 2>/dev/null || true

# Remove temporary files
git rm --cached -f *.tmp *.bak *.old 2>/dev/null || true

echo "Git cleanup complete"
