# MnMCP - MiniWorld Minecraft Connection Protocol

MnMCP is an open-source protocol bridge that enables seamless connection between MiniWorld game rooms and Minecraft servers.

## Features

- **Protocol Translation**: Converts between MiniWorld WebSocket protocol and Minecraft protocol
- **Multi-Language Support**: Core implementations in Python, Rust, Go, and TypeScript
- **Room Bridging**: Map MiniWorld rooms to Minecraft servers
- **Fake Authentication**: Local auth server for testing
- **Flexible Configuration**: YAML-based configuration with Clash integration
- **Cross-Platform**: Windows batch scripts for easy setup

## Quick Start

### Prerequisites

- Python 3.14+
- (Optional) Rust toolchain for Rust components
- (Optional) Go for Go server components
- (Optional) Node.js for web components

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MnMCP.git
cd MnMCP
```

2. Install Python dependencies:
```bash
pip install websockets aiohttp pyyaml
```

3. Run setup script (Administrator):
```bash
scripts\setup_and_start.bat
```

### Starting the Servers

1. Start HTTP Server:
```bash
python miniworld_http_server.py
```

2. Start WebSocket RPC Server:
```bash
python miniworld_rpc_server.py
```

3. Open MiniWorld and login with any credentials

## Project Structure

```
MnMCP/
├── mnmcp-v2/              # Main Python implementation v2
│   ├── main.py
│   ├── src/
│   │   ├── miniworld/     # MiniWorld protocol handlers
│   │   ├── crypto/        # XXTEA encryption
│   │   └── config.py
│   └── tests/
├── src/
│   ├── python/            # Python interceptors and servers
│   ├── rust/              # Rust core library
│   │   └── mnmcp-core/
│   ├── go/                # Go server implementation
│   │   └── mnmcp-server/
│   └── typescript/        # Web frontend
│       └── mnmcp-web/
├── scripts/               # Setup and utility scripts
├── config/                # Configuration files
│   └── clash_meta_*.yaml
└── docs/                  # Documentation
```

## Components

### Python Implementation (mnmcp-v2)

The main Python implementation providing:
- MiniWorld protocol parsing
- WebSocket message handling
- Room management
- Login simulation

### Rust Core (src/rust/mnmcp-core)

High-performance Rust library for:
- Protocol conversion
- Network handling
- Cryptographic operations

### Go Server (src/go/mnmcp-server)

Lightweight Go server implementation for production deployments.

### TypeScript Web (src/typescript/mnmcp-web)

Web-based management interface and monitoring dashboard.

## Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Architecture Overview](docs/architecture/)
- [Protocol Specification](docs/protocol/)

## Configuration

Edit `config/clash_meta_mnmcp_v3.yaml` to customize:
- Server endpoints
- Room mappings
- Proxy settings

## Development

### Running Tests

```bash
python -m pytest mnmcp-v2/tests/
```

### Building Rust Components

```bash
cd src/rust/mnmcp-core
cargo build --release
```

## License

GPL-3.0 License - See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Acknowledgments

- MiniWorld game community
- Minecraft protocol documentation
- Contributors and testers

---

**Made with ❤️ by the MnMCP Team**
