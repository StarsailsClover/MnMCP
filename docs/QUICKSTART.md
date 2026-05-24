# MnMCP v3.2 - No Clash Meta Needed!

**New Solution**: Pure Python proxy server - no external dependencies!

---

## What Changed

### Before (v3.1)
- ❌ Required Clash Meta (hard to download)
- ❌ Complex configuration
- ❌ External binary dependency

### Now (v3.2)
- ✅ Pure Python implementation
- ✅ No external downloads needed
- ✅ Simple to use

---

## Architecture

```
[MiniWorld Client]
    ↓ Set proxy: 127.0.0.1:7890
[MnMCP Proxy Server] (Python)
    ↓ Intercept openroom.mini1.cn
[MnMCP Fake API] (Python)
    ↓ Return fake room list
[MiniWorld shows Minecraft room]
```

---

## Quick Start

### Step 1: Start All Services

Run:
```
start_all.bat
```

This will open 2 windows:
1. **MnMCP Fake API** (Port 8080)
2. **MnMCP Proxy** (Port 7890)

**Keep both windows open!**

### Step 2: Set Proxy

Run as **Administrator**:
```
enable_proxy.bat
```

### Step 3: Test

1. Open MiniWorld 1.55.0
2. Click "Online"
3. Check room list

**Expected**: See room "Dissociate - Test"

---

## What Each Service Does

### 1. MnMCP Fake API (Port 8080)

**Purpose**: Pretend to be MiniWorld's room server

**Features**:
- Discovers Minecraft LAN rooms
- Returns fake room list with Minecraft rooms
- Handles MiniWorld API requests

**Log example**:
```
[LAN] Discovered Minecraft room: "Dissociate - Test"
[API] GET /server/room?cmd=server_config
[API] Returned room list: 1 room
```

### 2. MnMCP Proxy (Port 7890)

**Purpose**: Intercept and redirect traffic

**Features**:
- HTTP/HTTPS proxy
- Redirects openroom.mini1.cn → Fake API
- Redirects 42.240.175.30 → Fake API
- Forwards other traffic normally

**Log example**:
```
[GET] http://openroom.mini1.cn:8080/server/room
[INTERCEPT] Redirecting to fake API
```

---

## Testing Checklist

### Before Testing

- [ ] Minecraft Java opened LAN (you did this ✅)
- [ ] MiniWorld 1.55.0 ready
- [ ] Both services started
- [ ] Proxy enabled

### During Testing

Watch the logs:

**Fake API should show**:
```
[API] GET /server/room?cmd=server_config&uin=...
[API] Returned server_config
```

**Proxy should show**:
```
[GET] http://openroom.mini1.cn:8080/server/room
[INTERCEPT] Redirecting openroom.mini1.cn to fake API
```

### Success Indicators

1. ✅ Fake API receives requests
2. ✅ Proxy intercepts traffic
3. ✅ MiniWorld shows fake room

---

## Troubleshooting

### Issue: Proxy won't start

**Symptoms**:
```
[ERROR] Address already in use
```

**Solution**:
```powershell
# Kill process on port 7890
netstat -ano | findstr "7890"
taskkill /PID <PID> /F
```

### Issue: No API requests

**Symptoms**:
- Fake API shows no logs
- MiniWorld shows real rooms

**Possible causes**:
1. Proxy not started
2. System proxy not set
3. MiniWorld bypassed proxy

**Solutions**:
1. Check both windows are open
2. Run enable_proxy.bat again
3. Try Proxifier (force proxy)

### Issue: Connection refused

**Symptoms**:
```
[ERROR] Connection refused to 127.0.0.1:8080
```

**Solution**:
- Make sure Fake API is running
- Check port 8080 not blocked

---

## Files

```
workspace/
├── mnmcp_fake_api.py       <- Fake API server
├── mnmcp_proxy.py          <- Proxy server (NEW!)
├── start_all.bat           <- Start both services
├── enable_proxy.bat        <- Set system proxy
└── disable_proxy.bat       <- Unset proxy
```

---

## Current Status

```
✅ Fake API ready
✅ Proxy server ready
✅ Minecraft room discovered: "Dissociate - Test"
✅ No external downloads needed!
⏳ Ready to test
```

---

**Next**: Run `start_all.bat` and let's test!
