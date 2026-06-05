# Changelog

All notable changes to MnMCP will be documented in this file.

## [Victoria v3.1-20260605 Phase8 Stable] - 2026-06-05

### Added
- Complete CI/CD pipeline with GitHub Actions
- CONTRIBUTING.md for contributors
- Clean project structure
- Organized documentation

### Changed
- Rewrote README.md without emoji
- Updated all documentation
- Improved project organization

### Fixed
- GitHub Actions build errors
- Project structure issues

## [Victoria v3.0-20260605 Phase7 RC] - 2026-06-05

### Added
- MCPBridge core with 6-state state machine
- MCPMinecraftClient (TCP/MC protocol)
- MCPMiniClient (UDP/RakNet)
- 33+ unit tests with pytest
- Protocol codec with VarInt/String support
- 844 block mappings
- XXTEA/AES-CFB8 encryption
- HTTP proxy for testing
- RakNet gateway

### Changed
- Migrated from MN2MC to pure Python
- Improved code quality with type annotations

## [v3.26.0.0_dev Phase 1] - 2026-05-24

### Added
- Initial development version
- Basic protocol implementation
