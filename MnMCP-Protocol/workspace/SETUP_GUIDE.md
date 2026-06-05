# MnMCP v3.1 - Complete Setup Guide

---

## Step 1: Download Clash Meta

### Option A: Use Browser (Recommended)

1. Run this script:
   ```
   download_clash.bat
   ```
   It will open GitHub releases page

2. Download file:
   ```
   clash.meta-windows-amd64-compatible-v1.18.1.exe
   ```

3. Save to:
   ```
   D:\Coding\BlockConnect\BlockConnect-MnMCP\workspace\clash.meta.exe
   ```

### Option B: Direct Link

Download from:
```
https://github.com/MetaCubeX/Clash.Meta/releases/download/v1.18.1/clash.meta-windows-amd64-compatible-v1.18.1.exe
```

---

## Step 2: Start Services

### 2.1 Start Clash Meta

Run:
```
start_clash.bat
```

**Expected output**:
```
INFO[0000] Start initial compatible provider Default
INFO[0000] HTTP proxy listening at: 127.0.0.1:7890
INFO[0000] RESTful API listening at: 127.0.0.1:9090
```

**Keep this window open!**

### 2.2 Start Fake API Server

Already running! Check if you see:
```
[OK] API Server started: http://0.0.0.0:8080
[LAN] Discovered Minecraft room: "Dissociate - Test"
```

---

## Step 3: Set Proxy

Run as **Administrator**:
```
enable_proxy.bat
```

---

## Step 4: Test in MiniWorld

1. Open MiniWorld 1.55.0
2. Click "Online"
3. Check room list

**Expected**: See room "Dissociate - Test"

---

## Troubleshooting

### Issue: Clash Meta won't start

**Symptoms**:
```
[ERROR] clash.meta.exe not found!
```

**Solution**:
1. Make sure you downloaded the file
2. Rename it to `clash.meta.exe`
3. Put it in workspace folder

### Issue: Port already in use

**Symptoms**:
```
ERROR: listen tcp 127.0.0.1:7890: bind: address already in use
```

**Solution**:
```powershell
# Find process using port 7890
netstat -ano | findstr "7890"

# Kill the process
taskkill /PID <PID> /F
```

---

## Files Created

```
workspace/
├── clash.meta.exe              <- Download this
├── clash_meta_mnmcp_v3.yaml    <- Config (ready)
├── mnmcp_fake_api.py           <- Running
├── download_clash.bat          <- Helper script
├── start_clash.bat             <- Start Clash
├── enable_proxy.bat            <- Set proxy
└── disable_proxy.bat           <- Unset proxy
```

---

**Current Status**:
- ⏳ Waiting for Clash Meta download
- ✅ Fake API running
- ✅ Minecraft room discovered

**Next**: Download Clash Meta and start it!
