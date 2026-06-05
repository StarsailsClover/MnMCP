# MnMCP Workspace Reorganization Plan

## Current State

Too many files, mixed purposes, hard to navigate.

## Proposed Structure

```
D:\Coding\BlockConnect\BlockConnect-MnMCP\
│
├── workspace\                    # Development workspace
│   ├── src\                      # Source code
│   │   ├── python\               # Python implementations
│   │   │   ├── servers\          # Server implementations
│   │   │   │   ├── http_server.py
│   │   │   │   ├── ws_server.py
│   │   │   │   └── full_launcher.py
│   │   │   ├── interceptors\     # Traffic interception
│   │   │   │   ├── windivert.py
│   │   │   │   └── proxifier.py
│   │   │   └── utils\            # Utilities
│   │   │       ├── crypto.py
│   │   │       └── protocol.py
│   │   │
│   │   └── rust\                 # Rust implementations (future)
│   │       ├── Cargo.toml
│   │       └── src/
│   │
│   ├── config\                   # Configuration files
│   │   ├── hosts_backup\         # Hosts backups
│   │   ├── clash_meta\           # Clash Meta configs
│   │   └── proxifier\            # Proxifier profiles
│   │
│   ├── scripts\                  # Batch/PowerShell scripts
│   │   ├── setup\                # Setup scripts
│   │   │   ├── install_windivert.bat
│   │   │   ├── update_hosts.bat
│   │   │   └── install_deps.bat
│   │   ├── start\                # Start scripts
│   │   │   ├── start_servers.bat
│   │   │   └── start_capture.bat
│   │   └── utils\                # Utility scripts
│   │
│   ├── logs\                     # Log files
│   │   ├── proxifier\            # Proxifier logs
│   │   ├── mitmproxy\            # mitmproxy logs
│   │   └── windivert\            # WinDivert logs
│   │
│   ├── docs\                     # Documentation
│   │   ├── architecture\         # Architecture docs
│   │   ├── protocol\             # Protocol specs
│   │   └── guides\               # User guides
│   │
│   ├── tests\                    # Test files
│   │   └── test_protocols.py
│   │
│   └── tools\                    # External tools
│       ├── WinDivert\            # WinDivert binaries
│       └── mitmproxy\            # mitmproxy
│
├── BlockConnect-MnMCP\           # Main project (GitHub)
│   ├── src\                      # Source code
│   │   ├── core\                 # Core library
│   │   │   ├── Cargo.toml       # Rust core
│   │   │   └── src/
│   │   ├── bridge\               # Bridge implementations
│   │   │   ├── cpp\              # C++ implementation
│   │   │   ├── go\               # Go implementation
│   │   │   └── typescript\       # TypeScript implementation
│   │   └── cli\                  # CLI tools
│   │       └── Cargo.toml       # Rust CLI
│   │
│   ├── docs\                     # Documentation
│   ├── tests\                    # Tests
│   └── examples\                 # Examples
│
└── MnMCPResources\               # Original resources
    └── (keep as is)
```

## Multi-Language Implementation

### Core Components

| Component | Language | Reason |
|-----------|----------|--------|
| Network Stack | Rust | Performance, safety |
| Protocol Parser | Rust + C++ | Speed, binary handling |
| Encryption | Rust | Crypto libraries |
| CLI Tool | Rust | Cross-platform |
| Web UI | TypeScript | React/Vue frontend |
| Server Backend | Go | Concurrency, HTTP |
| Windows Driver | C++ | WinDivert integration |
| Python Bridge | Python | Rapid prototyping |

### Implementation Priority

1. **Phase 1: Python** (Current)
   - ✅ Working prototype
   - ✅ Protocol understanding
   - ⏳ Complete bridge

2. **Phase 2: Rust Core** (Next)
   - Network stack
   - Protocol parser
   - Encryption

3. **Phase 3: Multi-language**
   - Go server
   - TypeScript UI
   - C++ driver

## Team Expectations

### Feasibility: ✅ HIGH

**Why it works:**
- Rust for core: Industry standard for network tools
- Go for server: Easy deployment, good performance
- TypeScript for UI: Modern web dev
- C++ for driver: Required for WinDivert

**Challenges:**
- Team learning curve (Rust/Go)
- FFI complexity (Rust <-> C++)
- Build system complexity

### Recommendation

**Start with Rust core immediately!**

Benefits:
- Better performance than Python
- Memory safety
- Cross-platform
- Industry adoption

---

**Should we:**
1. Install WinDivert first
2. Then reorganize workspace
3. Then start Rust implementation?
