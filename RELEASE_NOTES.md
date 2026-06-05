<<<<<<< HEAD
# Victoria v3.1-20260605 Phase8 RC Release Notes

**Version**: Victoria v3.1-20260605 Phase8 RC  
**Date**: 2026-06-05  
**Status**: Release Candidate  
**Next**: Victoria Stable (after testing)
=======
# Victoria v3.1-20260605 Phase8 Stable Release Notes

**Version**: Victoria v3.1-20260605 Phase8 Stable  
**Date**: 2026-06-05  
**Status**: Stable
>>>>>>> 63e9a2631add1880056d6bc65b5e93f6d0af6126

---

## Overview

<<<<<<< HEAD
Victoria v3.1 Phase8 RC is a release candidate with clean project structure and CI/CD integration. This version is ready for testing before the stable release.

## Changes from Phase 7 RC

### Project Cleanup
- Added comprehensive .gitignore
- Removed redundant files from tracking
- Organized project structure
- Cleaned up documentation

### CI/CD
- Added GitHub Actions workflow
- Configured Python 3.9-3.12 testing
- Added coverage reporting
- Added linting (flake8, mypy)
=======
Victoria v3.1 Phase8 Stable is the first stable release of the MnMCP protocol bridge, featuring a complete implementation with CI/CD, clean documentation, and organized project structure.

## What's New

### Project Organization
- Clean file structure
- Organized documentation
- Removed redundant files
- Proper .gitignore

### CI/CD
- GitHub Actions workflow
- Automated testing on Python 3.9-3.12
- Coverage reporting
- Linting with flake8 and mypy
>>>>>>> 63e9a2631add1880056d6bc65b5e93f6d0af6126

### Documentation
- Rewrote README without emoji
- Added CONTRIBUTING.md
- Added CHANGELOG.md
<<<<<<< HEAD
- Updated RELEASE_NOTES

## Files Not in GitHub (via .gitignore)

### Development Resources
- 09-MnMCP-DevResources/
- 03-MnMCP-Protocol-Bridge/

### Version Update Docs
- PHASE*_EXECUTION_*.md
- PHASE*_PROGRESS_*.md
- MN3_*_REPORT.md
- INTEGRATION_*.md

### Archives
- archive/
- mnmcp-v2/

### Security
- .env
- config.yaml
=======
- Clear project structure

## Features

### Core Components
- Block mapping (844 blocks)
- XXTEA encryption
- AES-CFB8 encryption
- Protocol codec (82+ message types)
- Minecraft client (TCP)
- MiniWorld client (UDP/RakNet)
- Bridge core with bidirectional forwarding
- HTTP proxy and RakNet gateway

### Testing
- 33+ unit tests
- pytest configuration
- Coverage reporting
>>>>>>> 63e9a2631add1880056d6bc65b5e93f6d0af6126

## Installation

```bash
git clone https://github.com/StarsailsClover/MnMCP.git
cd MnMCP/mnmcp-v3-integrated
pip install -r requirements.txt
python verify_mn3.py
<<<<<<< HEAD
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Check coverage
python -m pytest --cov=src --cov-report=html
```

## Roadmap to Stable

| Task | Status | Target |
|------|--------|--------|
| Phase 8 RC | Done | 2026-06-05 |
| Testing | Pending | Next |
| Bug fixes | Pending | Next |
| Victoria Stable | Pending | After testing |

## Known Issues

See CHANGELOG.md for known issues.

---

**Victoria v3.1-20260605 Phase8 RC**  
*Release Candidate - Testing in Progress*
=======
```

## Quick Start

```python
from mcp_core import MCPBridge, MCPBridgeConfig

config = MCPBridgeConfig(
    mc_host="localhost",
    mc_port=25565,
    mc_username="BridgePlayer",
    mnw_uin=123456,
    mnw_passwd="password"
)

bridge = MCPBridge(config)
await bridge.start()
```

## Breaking Changes

None - this is the first stable release.

## Known Issues

- Block parsing not fully implemented
- Item sync not implemented
- Entity sync not implemented

## Contributors

MnMCP Team

## License

MIT License

---

**Victoria v3.1-20260605 Phase8 Stable**
>>>>>>> 63e9a2631add1880056d6bc65b5e93f6d0af6126
