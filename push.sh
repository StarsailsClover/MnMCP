#!/bin/bash
# Push cleaned repository to GitHub

echo "Pushing Victoria v3.1 Phase8 RC to GitHub..."
echo "=============================================="

# Push main branch
echo "1. Pushing main branch..."
git push origin main --force-with-lease
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to push main branch"
    exit 1
fi

# Remove old tag if exists
echo "2. Removing old tag..."
git tag -d "v3.1-20260605-phase8-rc" 2>/dev/null || true

# Create new tag
echo "3. Creating tag..."
git tag -a "v3.1-20260605-phase8-rc" -m "Victoria v3.1 Phase8 RC: Clean repository with 104 essential files

Changes:
- 710 files removed (87% reduction)
- 103,233 lines removed (96% reduction)
- Kept only essential: core code, tests, main docs, CI/CD
- Fixed CI workflow
- Fixed import errors
- Disabled Jekyll for Pages

Repository now contains:
- Core code: mnmcp-v3-integrated/src/
- Tests: tests/
- Docs: README, CHANGELOG, CONTRIBUTING, RELEASE_NOTES
- CI/CD: .github/workflows/ci.yml
- Config: .gitignore, requirements.txt, VERSION
- License: LICENSE"

# Push tag
echo "4. Pushing tag..."
git push origin "v3.1-20260605-phase8-rc" --force
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to push tag"
    exit 1
fi

echo ""
echo "=============================================="
echo "Push successful!"
echo ""
echo "Repository: https://github.com/StarsailsClover/MnMCP"
echo "Tag: v3.1-20260605-phase8-rc"
echo ""
echo "Files: 104"
echo "Lines: ~4,500"
echo "Status: Ready for testing"
