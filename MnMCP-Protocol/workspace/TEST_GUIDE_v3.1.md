# MnMCP v3.1 - Updated Test Guide

**Key Discovery**: MiniWorld room API uses port 8080, not 80/443!

---

## What I Found

From your resource files (HANDSHAKE_ANALYSIS_REPORT.md):

**Real API Endpoints**:
```
openroom.mini1.cn:8080/server/room?cmd=server_config
42.240.175.30:8080/server/room?cmd=query_map_player_count
```

**Key Parameters**:
- `cmd=server_config` - Get server configuration
- `cmd=query_map_player_count` - Query map player counts
- `uin` - User ID
- `auth` - Authentication signature
- `channel=110` - API ID (PC version)

---

## Updated Configuration

### 1. Clash Meta Config
- Added IP redirect: `42.240.175.30` → `127.0.0.1`
- Updated rules to intercept port 8080 traffic

### 2. Fake API Server
- Added `send_server_config()` handler
- Added `send_map_player_count()` handler
- Better request logging

---

## Current Status

**Running Services**:
- ✅ Fake API Server: Port 8080
- ✅ Minecraft LAN Discovery: Active
- ✅ Discovered Room: "Dissociate - Test" (192.168.1.7:54056)

---

## Testing Steps

### Step 1: Start Clash Meta

You need to download and start Clash Meta first!

**Download**:
```
https://github.com/MetaCubeX/Clash.Meta/releases
```

**Start**:
```powershell
cd D:\Coding\BlockConnect\BlockConnect-MnMCP\workspace
clash.meta-windows-amd64.exe -f clash_meta_mnmcp_v3.yaml
```

### Step 2: Verify Fake API

Check if it's running:
```
http://127.0.0.1:8080/server/room?cmd=server_config
```

Should return JSON response.

### Step 3: Set System Proxy

Run as Administrator:
```
enable_proxy.bat
```

Or manually:
```powershell
netsh winhttp set proxy 127.0.0.1:7890
```

### Step 4: Test in MiniWorld

1. Open MiniWorld 1.55.0
2. Click "Online"
3. Check room list

---

## Expected Behavior

### If Proxy Works

Fake API should log:
```
[API] GET /server/room?cmd=server_config&uin=...
[API] Query params: {'cmd': ['server_config'], 'uin': [...]}
[API] Returned server_config
```

### If Room List Works

You should see:
```
Room: Dissociate - Test
Players: 1/20
```

---

## Troubleshooting

### Issue: No API Requests

**Symptoms**:
- Fake API shows no logs
- MiniWorld shows real rooms

**Possible Causes**:
1. Clash Meta not started
2. Proxy not set correctly
3. MiniWorld bypassed proxy

**Solutions**:
1. Start Clash Meta first
2. Check proxy settings
3. Use Proxifier to force proxy

### Issue: Wrong Port

**Symptoms**:
- Connection refused
- Port 80/443 errors

**Solution**:
- MiniWorld uses port 8080, not 80!
- Make sure Fake API listens on 8080

---

## Next Steps

1. **Start Clash Meta** (most important!)
2. Set proxy
3. Test and report results

---

**Current blocker**: Need to start Clash Meta for proxy to work!
