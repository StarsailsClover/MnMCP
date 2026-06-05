# MnMCP v7.0 - Clash Meta TUN Mode Strategy

## Problem

- Windows 11 hosts file not working reliably
- System proxy bypassed by some applications
- Need a more reliable interception method

## Solution: Clash Meta TUN Mode

TUN mode creates a virtual network interface that captures ALL traffic:
- ✅ Works on Windows 11
- ✅ Captures traffic that bypasses system proxy
- ✅ No hosts file modifications needed
- ✅ More reliable than Proxifier

## How TUN Mode Works

```
[MiniWorld Client]
    │
    ▼
[Windows Network Stack]
    │
    ▼
[Clash Meta TUN Interface] ← Virtual network adapter
    │
    ├─ Intercepts ALL packets
    ├─ Applies routing rules
    │
    ├─ MiniWorld traffic → Local servers
    └─ Other traffic → Direct/Proxy
    │
    ▼
[MnMCP Local Servers]
    ├─ HTTP Server (Port 8080)
    └─ WebSocket Server (Port 8081)
```

## Setup Steps

### 1. Download Clash Meta

Download latest release:
```
https://github.com/MetaCubeX/Clash.Meta/releases
```

File: `clash.meta-windows-amd64-compatible.exe`

### 2. Place in Workspace

Copy to:
```
D:\Coding\BlockConnect\BlockConnect-MnMCP\workspace\clash.meta.exe
```

### 3. Start Clash Meta with TUN

```cmd
cd D:\Coding\BlockConnect\BlockConnect-MnMCP\workspace
clash.meta.exe -f clash_meta_tun.yaml
```

### 4. Start MnMCP Servers

```cmd
cd D:\Coding\BlockConnect\BlockConnect-MnMCP\workspace
start_servers_fixed.bat
```

### 5. Test

1. Open MiniWorld
2. Login
3. Check room list

## Configuration

### clash_meta_tun.yaml

```yaml
tun:
  enable: true
  stack: system
  dns-hijack:
    - 8.8.8.8:53
  auto-route: true

dns:
  enable: true
  enhanced-mode: fake-ip

rules:
  - DOMAIN-SUFFIX,mini1.cn,MiniWorld
  - IP-CIDR,42.240.175.30/32,MiniWorld
  - MATCH,DIRECT
```

## Advantages

1. ✅ No hosts file needed
2. ✅ Works on Windows 11
3. ✅ Captures all traffic
4. ✅ DNS hijacking
5. ✅ Automatic routing

## Next Steps

1. Download Clash Meta
2. Place in workspace
3. Run: `clash.meta.exe -f clash_meta_tun.yaml`
4. Start MnMCP servers
5. Test with MiniWorld

---

**This is the most reliable method for Windows 11!** 🎯
