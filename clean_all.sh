#!/bin/bash
# Remove all non-essential files from git

echo "Cleaning repository..."

# Remove directories
git rm -r --cached -f "09-MnMCP-DevResources" 2>/dev/null || true
git rm -r --cached -f "MnMCP-Protocol" 2>/dev/null || true
git rm -r --cached -f "mnmcp-v2" 2>/dev/null || true
git rm -r --cached -f "03-MnMCP-Protocol-Bridge" 2>/dev/null || true
git rm -r --cached -f "archive" 2>/dev/null || true

# Remove old docs
git rm --cached -f PHASE*.md 2>/dev/null || true
git rm --cached -f TEST_*.md 2>/dev/null || true
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

# Remove scripts
git rm -r --cached -f "scripts" 2>/dev/null || true
git rm --cached -f clean_git.sh 2>/dev/null || true
git rm --cached -f clean_all.sh 2>/dev/null || true

# Remove other
.git rm --cached -f .gitattributes 2>/dev/null || true

echo "Done"
