# MnMCP Project Structure

**Version**: Victoria v3.1-20260605 Phase8 Stable

```
MnMCP/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI
│
├── mnmcp-v3-integrated/        # Main project
│   ├── src/
│   │   ├── mcp_mapping/        # Block mappings
│   │   ├── mcp_crypto/         # Encryption
│   │   ├── mcp_protocol/       # Protocol codec
│   │   ├── mcp_mc/             # Minecraft client
│   │   ├── mcp_mini/           # MiniWorld client
│   │   ├── mcp_core/           # Bridge core
│   │   └── mcp_proxy/          # Proxy/Gateway
│   ├── tests/
│   │   ├── unit/               # Unit tests
│   │   ├── integration/          # Integration tests
│   │   └── system/             # System tests
│   ├── requirements.txt        # Dependencies
│   ├── VERSION                 # Version file
│   └── verify_mn3.py          # Verification script
│
├── docs/                       # Documentation
│   ├── architecture/             # Architecture docs
│   ├── api/                      # API reference
│   └── guides/                   # User guides
│
├── archive/                    # Archived files
│   └── phase8_cleanup/           # Pre-cleanup files
│
├── scripts/                    # Utility scripts
│   └── archive_old_files.py      # Cleanup script
│
├── .gitignore                  # Git ignore rules
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guide
├── LICENSE                     # MIT License
├── README.md                   # Project readme
└── RELEASE_NOTES.md            # Release notes
```

## Key Files

| File | Purpose |
|------|---------|
| README.md | Project overview |
| CHANGELOG.md | Version history |
| CONTRIBUTING.md | How to contribute |
| RELEASE_NOTES.md | Release details |
| .github/workflows/ci.yml | CI/CD configuration |
| requirements.txt | Python dependencies |
| VERSION | Current version |

## Source Code

| Module | Purpose | Lines |
|--------|---------|-------|
| mcp_mapping | Block ID mappings | ~800 |
| mcp_crypto | Encryption (XXTEA, AES) | ~400 |
| mcp_protocol | Protocol definitions | ~800 |
| mcp_mc | Minecraft client | ~2000 |
| mcp_mini | MiniWorld client | ~600 |
| mcp_core | Bridge core | ~500 |
| mcp_proxy | Proxy/Gateway | ~600 |

## Tests

| Type | Count | Location |
|------|-------|----------|
| Unit | 33+ | tests/unit/ |
| Integration | 0+ | tests/integration/ |
| System | 0+ | tests/system/ |
