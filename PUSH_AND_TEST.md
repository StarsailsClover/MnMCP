# Push and Test Instructions

**Date**: 2026-06-06  
**Version**: Victoria v3.1-20260605 Phase8 RC

---

## Step 1: Push to GitHub

When network is restored, run:

### Option A: Automated Script

```bash
# Windows
call scripts\dev\push.bat

# Linux/Mac
bash scripts/dev/push.sh
```

### Option B: Manual Push

```bash
# 1. Push main branch
git push origin main --force-with-lease

# 2. Create tag
git tag -d "v3.1-20260605-phase8-rc" 2>/dev/null || true
git tag -a "v3.1-20260605-phase8-rc" -m "Victoria v3.1 Phase8 RC: Clean repository with 94 essential files"

# 3. Push tag
git push origin "v3.1-20260605-phase8-rc"
```

---

## Step 2: Verify CI/CD

Visit: https://github.com/StarsailsClover/MnMCP/actions

Expected:
- [ ] Pages build: Pass
- [ ] CI test (3.9): Pass
- [ ] CI test (3.10): Pass
- [ ] CI test (3.11): Pass
- [ ] CI test (3.12): Pass
- [ ] CI lint: Pass

---

## Step 3: Run Tests

### Quick Verification

```bash
cd mnmcp-v3-integrated
python verify_mn3.py
```

Expected: `10/10 通过 (100%)`

### Full Test Suite

```bash
# Install dependencies
pip install pyyaml

# Run all tests
python -m pytest tests/ -v

# Check coverage
python -m pytest --cov=src --cov-report=html
```

---

## Step 4: Manual Testing

### Test 1: Block Mapping

```bash
python -c "import sys; sys.path.insert(0, 'src'); from mcp_mapping.blocks_integrated import BlockMapperIntegrated; m = BlockMapperIntegrated(); print('Mappings:', m.get_stats()['total_mappings'])"
```

Expected: `Mappings: 56`

### Test 2: Protocol

```bash
python -c "import sys; sys.path.insert(0, 'src'); from mcp_protocol.codec import MCPProtocolCodec, PacketDirection; c = MCPProtocolCodec(); p = c.create_packet(9001, b'test', PacketDirection.CLIENT_TO_SERVER); print('Message:', p.get_message_name())"
```

Expected: `Message: PB_ChatContentCH`

### Test 3: Bridge Core

```bash
python -c "import sys; sys.path.insert(0, 'src'); from mcp_core.bridge import MCPBridge, MCPBridgeConfig; b = MCPBridge(MCPBridgeConfig()); print('Bridge OK'); print('Yaw 0 ->', b._mc_yaw_to_mnw(0))"
```

Expected:
```
Bridge OK
Yaw 0 -> 180
```

---

## Step 5: Test Report

Document results in `TEST_REPORT.md`:

```markdown
# Test Report - Victoria v3.1 Phase8 RC

**Date**: 2026-06-06

## Results

| Test | Status | Notes |
|------|--------|-------|
| verify_mn3.py | ✅/❌ | |
| pytest | ✅/❌ | |
| Block mapping | ✅/❌ | |
| Protocol | ✅/❌ | |
| Bridge | ✅/❌ | |

## Issues

- Issue 1: ...
- Issue 2: ...

## Conclusion

Ready for Stable / Needs fixes
```

---

## Step 6: Fix Issues (if any)

1. Fix code
2. Test again
3. Commit: `git commit -m "Fix: ..."`
4. Push: `git push origin main`

---

## Step 7: Release Stable

When all tests pass:

```bash
# Update version
echo "Victoria v3.1-20260606 Phase8 Stable" > mnmcp-v3-integrated/VERSION

# Commit
git add mnmcp-v3-integrated/VERSION
git commit -m "Release Victoria v3.1 Stable"

# Tag
git tag -a "v3.1-20260606-stable" -m "Victoria v3.1 Stable"
git push origin main
git push origin "v3.1-20260606-stable"
```

---

## Summary

| Step | Action | Status |
|------|--------|--------|
| 1 | Push to GitHub | Pending |
| 2 | Verify CI/CD | Pending |
| 3 | Run tests | Pending |
| 4 | Manual testing | Pending |
| 5 | Test report | Pending |
| 6 | Fix issues | If needed |
| 7 | Release Stable | Final |

---

**Ready for push and testing!**
