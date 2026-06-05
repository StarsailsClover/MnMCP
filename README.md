# MnMCP

**MiniWorld Connection Protocol**

A protocol bridge allowing Minecraft Java Edition clients to connect to MiniWorld servers.

**Version**: Victoria v3.0-20260605 Phase8 Stable  
**Date**: 2026-06-05

---

## Overview

MnMCP is a protocol bridge that enables Minecraft Java Edition clients to connect to MiniWorld servers. It translates protocols between the two games, allowing seamless cross-platform gameplay.

### Key Features

- Pure Python implementation
- Type-safe with full type annotations
- Modular architecture
- Async/await support
- Comprehensive test suite

---

## Project Structure

```
MnMCP/
├── mnmcp-v3-integrated/       # Main project
│   ├── src/
│   │   ├── mcp_mapping/      # Block mappings (844 blocks)
│   │   ├── mcp_crypto/       # Encryption (XXTEA, AES-CFB8)
│   │   ├── mcp_protocol/     # Protocol definitions
│   │   ├── mcp_mc/           # Minecraft client
│   │   ├── mcp_mini/         # MiniWorld client
│   │   ├── mcp_core/         # Bridge core
│   │   └── mcp_proxy/        # Proxy/Gateway
│   ├── tests/                  # Test suite
│   └── verify_mn3.py         # Verification script
├── docs/                       # Documentation
└── README.md                   # This file
```

---

## Installation

### Requirements

- Python 3.9+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Verify Installation

```bash
cd mnmcp-v3-integrated
python verify_mn3.py
```

---

## Quick Start

### Using the Bridge

```python
import asyncio
from mcp_core import MCPBridge, MCPBridgeConfig

async def main():
    config = MCPBridgeConfig(
        mc_host="localhost",
        mc_port=25565,
        mc_username="BridgePlayer",
        mnw_uin=123456,
        mnw_passwd="your_password"
    )
    
    bridge = MCPBridge(config)
    
    # Start bridge
    if await bridge.start():
        print("Bridge started successfully!")
        
        # Run until interrupted
        while bridge.is_running:
            await asyncio.sleep(1)
    
    # Stop bridge
    await bridge.stop()

asyncio.run(main())
```

---

## Architecture

### Core Components

1. **mcp_mapping**: Block ID mappings between MC and MNW
2. **mcp_crypto**: Encryption layers (XXTEA for MNW, AES-CFB8 for MC)
3. **mcp_protocol**: Protocol codec with 82+ message types
4. **mcp_mc**: Minecraft protocol client (TCP)
5. **mcp_mini**: MiniWorld protocol client (UDP/RakNet)
6. **mcp_core**: Bridge core with bidirectional forwarding
7. **mcp_proxy**: HTTP proxy and RakNet gateway

### Data Flow

```
Minecraft Client <--TCP--> MCPBridge <--UDP--> MiniWorld Server
                                 |
                                 v
                          Protocol Translation
```

---

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

### Project Statistics

- Core code: ~4,000 lines
- Test code: ~400 lines
- Documentation: ~2,500 lines
- Total: ~6,900 lines

---

## Version History

### Victoria v3.0-20260605 Phase8 Stable
- Complete bridge core
- 33+ unit tests
- CI/CD integration
- Clean project structure

### Victoria v3.0-20260605 Phase7 RC
- Initial release candidate
- Basic bridge functionality

---

## Contributing

See CONTRIBUTING.md for guidelines.

---

## License

MIT License

---

## Acknowledgments

- MN2MC project for protocol reverse engineering
- MiniWorld community for API documentation
- Minecraft protocol documentation (wiki.vg)
