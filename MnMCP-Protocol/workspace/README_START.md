# MnMCP - Quick Start Guide

## Prerequisites

✅ Python 3.14 installed  
✅ websockets installed  
✅ All server scripts ready

## Start Servers (Manual Steps)

### Step 1: Modify Hosts File (Administrator)

**Option A: Run as Administrator**

1. Right-click `setup_and_start.bat`
2. Select "Run as administrator"
3. Click "Yes" on UAC prompt

**Option B: Manual Edit**

1. Open Notepad as Administrator
2. Open: `C:\Windows\System32\drivers\etc\hosts`
3. Add these lines at the end:

```
# MnMCP - MiniWorld Server Redirection
127.0.0.1 openroom.mini1.cn
127.0.0.1 shequ.mini1.cn
127.0.0.1 125.88.252.175
127.0.0.1 42.240.175.30
127.0.0.1 1.13.213.183
127.0.0.1 1.13.213.198
127.0.0.1 1.13.213.236
```

4. Save file
5. Run in CMD: `ipconfig /flushdns`

### Step 2: Start Servers

**Open TWO Command Prompt windows:**

**Window 1 - HTTP Server:**
```cmd
cd D:\Coding\BlockConnect\BlockConnect-MnMCP\workspace
C:\Users\Sails\AppData\Local\Programs\Python\Python314\python.exe miniworld_http_server.py
```

**Window 2 - WebSocket RPC Server:**
```cmd
cd D:\Coding\BlockConnect\BlockConnect-MnMCP\workspace
C:\Users\Sails\AppData\Local\Programs\Python\Python314\python.exe miniworld_rpc_server.py
```

### Step 3: Test

1. **Close Proxifier** (not needed anymore)
2. **Open MiniWorld**
3. **Login** with any account (fake auth)
4. **Check room list** - you should see "🎮 Minecraft Server"!

## Expected Results

### HTTP Server Window
```
[OK] HTTP server started on 127.0.0.1:8080
[HTTP] GET /server/room?cmd=server_config
  → Sent server_config
[HTTP] GET /room/list
  → Sent room_list with Minecraft room!
```

### WebSocket RPC Window
```
[OK] Starting on ws://127.0.0.1:8081
[+] Client 12345 connected
[1] RPC: login.auth (seq=1)
  → Login authentication
[2] RPC: baseinfo.update (seq=2)
  → Update base info
[3] RPC: room.list (seq=3)
  → Get room list
  → Injecting 2 rooms (including Minecraft!)
```

### MiniWorld
- Login: Success (fake account)
- Room list: Shows "🎮 Minecraft Server"
- Can join: Will connect to Minecraft LAN

## Troubleshooting

### Issue: "Please run as Administrator"

**Solution**: Right-click → "Run as administrator"

### Issue: "Address already in use"

**Solution**: 
```cmd
netstat -ano | findstr "8080"
taskkill /PID <PID> /F
```

### Issue: MiniWorld still connects to real server

**Solution**:
1. Check hosts file is saved
2. Run: `ipconfig /flushdns`
3. Restart MiniWorld
4. Check: `ping shequ.mini1.cn` should return 127.0.0.1

### Issue: Can't login

**Solution**: 
- Use any username/password (fake auth)
- Server accepts all credentials

---

**Ready? Start with Step 1 (Modify hosts file)!** 🚀
