# MnMCP - Complete mitmproxy Setup Guide

## Step-by-Step Installation

### Step 1: Install Python (5 minutes)

1. **Download Python 3.11**
   - Visit: https://www.python.org/downloads/
   - Download: "Python 3.11.x Windows installer (64-bit)"

2. **Install Python**
   - Run the installer
   - ✅ **IMPORTANT**: Check "Add Python to PATH"
   - Click "Install Now"
   - Wait for installation to complete

3. **Verify Installation**
   ```cmd
   python --version
   ```
   Should show: `Python 3.11.x`

---

### Step 2: Install mitmproxy (5-10 minutes)

1. **Run installation script**
   ```
   install_mitmproxy.bat
   ```
   
   Or manually:
   ```cmd
   python -m pip install --upgrade pip
   python -m pip install mitmproxy
   ```

2. **Verify Installation**
   ```cmd
   mitmdump --version
   ```
   Should show: `Mitmproxy: x.x.x`

---

### Step 3: Install mitmproxy Certificate (2 minutes)

**Why?** To decrypt HTTPS/WebSocket traffic

1. **Start mitmproxy**
   ```
   start_mitmproxy.bat
   ```

2. **Open browser**
   - Visit: http://mitm.it
   - You should see mitmproxy certificate page

3. **Download Certificate**
   - Click "Windows"
   - Download `mitmproxy-ca-cert.p12`

4. **Install Certificate**
   - Double-click the downloaded file
   - Store Location: "Local Machine"
   - Click "Next"
   - Password: (leave empty)
   - Certificate Store: "Place all certificates in the following store"
   - Click "Browse" → Select "Trusted Root Certification Authorities"
   - Click "Next" → "Finish"
   - Click "Yes" on security warning

5. **Verify**
   - Open "certmgr.msc"
   - Go to "Trusted Root Certification Authorities" → "Certificates"
   - Look for "mitmproxy"

---

### Step 4: Configure Proxifier (1 minute)

1. **Update Proxy Server**
   - Profile → Proxy Servers
   - Edit existing proxy or add new:
     - Address: 127.0.0.1
     - Port: 8080
     - Protocol: HTTP
   - Click "OK"

2. **Verify Rule**
   - Profile → Proxification Rules
   - Make sure minigameapp.exe rule exists
   - Action: Use proxy (127.0.0.1:8080)

---

### Step 5: Test (2 minutes)

1. **Start mitmproxy**
   ```
   start_mitmproxy.bat
   ```
   
   You should see:
   ```
   Proxy server listening at http://127.0.0.1:8080
   ```

2. **Open MiniWorld**
   - Click "Online"
   - Go to room list

3. **Check mitmproxy Output**
   
   You should see:
   ```
   [WebSocket] Connection to: 125.88.252.175
   [1] → Server
   Type: Text
   JSON Content:
   {
     "type": "room_list",
     "data": [...]
   }
   ```

---

## Expected Output

### Successful Connection

```
============================================================
[WebSocket] Connection to: 125.88.252.175
[WebSocket] Path: /ws/room
[WebSocket] Headers: {...}
============================================================

[1] ← Client
Type: Text
Length: 1234 bytes
JSON Content:
{
  "type": "room_list",
  "data": [
    {
      "room_id": "123456",
      "room_name": "Test Room",
      "players": 2,
      "max_players": 6
    }
  ]
}

🎯 FOUND ROOM LIST MESSAGE!
============================================================
✅ Injected Minecraft room!
```

---

## Troubleshooting

### Issue 1: Python not found

**Symptom**: `'python' is not recognized`

**Solution**:
1. Reinstall Python
2. Make sure "Add to PATH" is checked
3. Restart terminal

### Issue 2: pip not found

**Symptom**: `No module named pip`

**Solution**:
```cmd
python -m ensurepip --upgrade
```

### Issue 3: mitmproxy not found

**Symptom**: `'mitmdump' is not recognized`

**Solution**:
1. Check if installed: `python -m pip list | findstr mitmproxy`
2. Reinstall: `python -m pip install --force-reinstall mitmproxy`
3. Add to PATH: `C:\Users\<YourName>\AppData\Local\Programs\Python\Python311\Scripts`

### Issue 4: Certificate not working

**Symptom**: SSL errors in mitmproxy

**Solution**:
1. Uninstall old certificate
2. Reinstall from http://mitm.it
3. Make sure installed to "Trusted Root"
4. Restart MiniWorld

### Issue 5: No WebSocket messages

**Symptom**: mitmproxy shows connections but no messages

**Solution**:
1. Check Proxifier is routing minigameapp.exe
2. Check proxy is 127.0.0.1:8080
3. Restart MiniWorld
4. Try refreshing room list

---

## Quick Start Commands

```cmd
# Install
install_mitmproxy.bat

# Start
start_mitmproxy.bat

# Test certificate
start http://mitm.it

# Check if running
netstat -ano | findstr "8080"
```

---

## Files

```
workspace/
├── install_mitmproxy.bat              ← Run this first
├── start_mitmproxy.bat                ← Then run this
├── mnmcp_websocket_interceptor.py     ← mitmproxy script
└── MITMPROXY_SETUP_GUIDE.md           ← This guide
```

---

## Timeline

- Python installation: 5 min
- mitmproxy installation: 5-10 min
- Certificate installation: 2 min
- Configuration: 1 min
- Testing: 2 min

**Total: ~15-20 minutes**

---

## Next Steps After Installation

1. ✅ Python installed
2. ✅ mitmproxy installed
3. ✅ Certificate installed
4. ✅ Proxifier configured
5. ⏳ **Test with MiniWorld**
6. ⏳ **Capture room list**
7. ⏳ **Inject Minecraft room**
8. ⏳ **Test end-to-end**

---

**Ready? Run `install_mitmproxy.bat` to start!** 🚀
