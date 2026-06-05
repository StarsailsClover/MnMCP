# MnMCP - Diagnostic Checklist

## Current Status

### Services Running
- [ ] Clash Meta TUN
- [ ] HTTP Server (Port 8080)
- [ ] WebSocket Server (Port 8081)

### Problem
- MiniWorld not connecting through proxy
- No traffic captured
- "参数错误" on login

## Possible Causes

### 1. Port Conflict
Multiple processes using port 8080

**Check**:
```cmd
netstat -ano | findstr "8080"
```

**Fix**: Kill conflicting processes

### 2. Clash Meta Not Intercepting
TUN mode not working or misconfigured

**Check**:
- Is TUN interface created?
- Are routes added?
- Is DNS hijacking working?

### 3. MiniWorld Bypassing
MiniWorld using hardcoded IPs or bypassing proxy

**Check**:
- Does ping to mini1.cn return 198.18.x.x? (fake-ip)
- Is MiniWorld process visible in Clash Meta?

### 4. Wrong Protocol
MiniWorld might use QUIC/HTTP3 instead of HTTP/HTTPS

## Diagnostic Steps

### Step 1: Verify Clash Meta TUN

1. Check TUN interface:
   ```cmd
   ipconfig /all | findstr "TUN"
   ```

2. Check routes:
   ```cmd
   route print | findstr "198.18"
   ```

3. Test DNS:
   ```cmd
   nslookup shequ.mini1.cn
   ```
   Should return: 198.18.x.x (fake-ip)

### Step 2: Test HTTP Server

```cmd
curl http://127.0.0.1:8080/server/room?cmd=server_config
```

Should return JSON response.

### Step 3: Check MiniWorld Connections

```cmd
netstat -ano | findstr "minigameapp"
```

See where MiniWorld is connecting.

## Alternative Approach

Since TUN mode is complex, let's try **direct connection**:

### Option A: Use Real Minecraft Server

1. Start Minecraft LAN
2. Note the port (e.g., 54321)
3. Create room that points directly to Minecraft

### Option B: Packet-Level Interception

Use WinDivert to capture and modify packets at network driver level.

### Option C: DLL Injection

Inject code into MiniWorld to hook network functions.

## Recommendation

Given the difficulties, I recommend:

**SIMPLIFIED APPROACH**:

Instead of intercepting MiniWorld traffic, let's:

1. **Start Minecraft LAN** (you already did this)
2. **Create a simple proxy** that listens on a port
3. **Manually tell MiniWorld to connect** to that port
4. **Translate protocols** between MiniWorld and Minecraft

This bypasses all the interception complexity!

---

**What do you think? Should we try the simplified approach?**
