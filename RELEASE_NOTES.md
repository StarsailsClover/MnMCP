# Victoria v3.1-20260605 Phase8 Stable Release Notes

**Version**: Victoria v3.1-20260605 Phase8 Stable  
**Date**: 2026-06-05  
**Status**: Stable

---

## Overview

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

### Documentation
- Rewrote README without emoji
- Added CONTRIBUTING.md
- Added CHANGELOG.md
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

## Installation

```bash
git clone https://github.com/StarsailsClover/MnMCP.git
cd MnMCP/mnmcp-v3-integrated
pip install -r requirements.txt
python verify_mn3.py
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
