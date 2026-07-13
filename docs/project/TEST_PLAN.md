# MnMCP Victoria v3.1 Phase8 RC Test Plan

**Version**: Victoria v3.1-20260605 Phase8 RC  
**Date**: 2026-06-05  
**Status**: Testing

---

## Test Objectives

Verify MnMCP Phase8 RC functionality before Stable release.

## Test Scope

### 1. Unit Tests

| Module | Test File | Cases | Status |
|--------|-----------|-------|--------|
| Mapping | test_mapping.py | 8 | Ready |
| Crypto | test_crypto.py | 5 | Ready |
| Protocol | test_protocol.py | 10 | Ready |
| MC Client | test_mc_client.py | 4 | Ready |
| Mini Client | test_mini_client.py | 4 | Ready |
| Bridge | test_bridge.py | 6 | Ready |
| **Total** | | **37** | |

### 2. Integration Tests

| Test | Description | Status |
|------|-------------|--------|
| test_mc_connection | MC client connection | Pending |
| test_mnw_connection | MNW client connection | Pending |
| test_bridge_start | Bridge startup | Pending |
| test_position_sync | Position synchronization | Pending |

### 3. Manual Tests

| Test | Steps | Expected |
|------|-------|----------|
| Install | pip install -r requirements.txt | Success |
| Verify | python verify_mn3.py | All pass |
| Unit | python -m pytest tests/ | 37 pass |
| Import | from mcp_core import MCPBridge | Success |

---

## Test Environment

### Requirements

```bash
Python 3.9+
pip
Git
```

### Setup

```bash
git clone https://github.com/StarsailsClover/MnMCP.git
cd MnMCP/mnmcp-v3-integrated
pip install -r requirements.txt
```

### Run Tests

```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest --cov=src --cov-report=html

# Specific module
python -m pytest tests/unit/test_mapping.py -v
```

---

## Test Schedule

| Phase | Duration | Status |
|-------|----------|--------|
| Unit Tests | 1 hour | Ready |
| Integration Tests | 2 hours | Pending |
| Manual Tests | 1 hour | Pending |
| Bug Fixes | As needed | - |
| Re-test | 1 hour | - |

---

## Acceptance Criteria

- [ ] All 37 unit tests pass
- [ ] Coverage >= 70%
- [ ] No critical bugs
- [ ] Documentation complete
- [ ] CI/CD passes

---

## Test Results

| Test | Result | Notes |
|------|--------|-------|
| | | |

---

## Release Decision

| Criteria | Status | Decision |
|----------|--------|----------|
| Tests Pass | | |
| No Blockers | | |
| **Release** | | **Victoria Stable** |
