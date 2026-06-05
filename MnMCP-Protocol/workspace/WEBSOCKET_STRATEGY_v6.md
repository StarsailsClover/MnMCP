# MnMCP v6.0 - WebSocket Interception Strategy

**Based on packet capture findings: MiniWorld uses TCP/WebSocket!**

---

## What We Discovered

From packet capture:
- ✅ MiniWorld uses **TCP**, not UDP
- ✅ Port **8081** on `125.88.252.175` (shequ.mini1.cn)
- ✅ Traffic is **TLS encrypted**
- ✅ Protocol is **WebSocket** over HTTPS

---

## New Architecture

```
[MiniWorld Client]
    │
    ├─ Set proxy: 127.0.0.1:8080
    │
    ▼
[mitmproxy] (Port 8080)
    │
    ├─ Intercepts HTTPS/WebSocket
    ├─ Decrypts TLS
    ├─ Monitors WebSocket messages
    │
    ├─ Detects room list message
    ├─ Injects Minecraft room
    │
    └─ Forwards to real server
    
[Real Server] (125.88.252.175:8081)
```

---

## Implementation

### Tool: mitmproxy

**Why mitmproxy?**
- ✅ Professional HTTPS/WebSocket interceptor
- ✅ Handles TLS automatically
- ✅ Python scripting support
- ✅ Easy to use

### Setup Steps

1. **Install mitmproxy**
   ```bash
   pip install mitmproxy
   ```

2. **Install certificate**
   - Start mitmproxy
   - Visit http://mitm.it
   - Download Windows certificate
   - Install to "Trusted Root Certification Authorities"

3. **Run interceptor**
   ```bash
   mitmdump -s mnmcp_websocket_interceptor.py
   ```

4. **Configure proxy**
   - Use Proxifier: Route minigameapp.exe → 127.0.0.1:8080
   - Or system proxy: 127.0.0.1:8080

---

## How It Works

### 1. WebSocket Connection

```
Client → mitmproxy → Server
         ↓
    Intercepts handshake
    Establishes two connections:
    - Client ↔ mitmproxy
    - mitmproxy ↔ Server
```

### 2. Message Flow

```
Server → Room list message → mitmproxy
                              ↓
                         Detects room list
                              ↓
                         Injects Minecraft room
                              ↓
                         Modified message → Client
```

### 3. Room Injection

```python
# Original message
{
  "type": "room_list",
  "data": [
    {"room_id": "123", "name": "Room 1"},
    {"room_id": "456", "name": "Room 2"}
  ]
}

# Modified message
{
  "type": "room_list",
  "data": [
    {"room_id": "999999999", "name": "🎮 Minecraft Server"},  ← Injected!
    {"room_id": "123", "name": "Room 1"},
    {"room_id": "456", "name": "Room 2"}
  ]
}
```

---

## Advantages

1. ✅ **No need for UDP/RakNet** - WebSocket is simpler
2. ✅ **Automatic TLS handling** - mitmproxy handles encryption
3. ✅ **Message-based** - Easy to parse JSON
4. ✅ **Real-time injection** - Modify messages on-the-fly
5. ✅ **Debugging** - See all WebSocket traffic

---

## Testing Plan

### Phase 1: Capture Messages (Today)

1. Start mitmproxy
2. Configure Proxifier
3. Open MiniWorld
4. Capture WebSocket messages
5. Find room list format

### Phase 2: Inject Room (Tomorrow)

1. Identify room list message
2. Implement injection logic
3. Test if room appears
4. Verify room details

### Phase 3: Bridge to Minecraft (Day 3)

1. Handle room join
2. Connect to Minecraft LAN
3. Protocol translation
4. End-to-end test

---

## Files Created

```
workspace/
├── mnmcp_websocket_interceptor.py  ← mitmproxy script
├── start_websocket_interceptor.bat ← Setup and start
└── WEBSOCKET_STRATEGY_v6.md        ← This document
```

---

## Next Steps

1. **Install mitmproxy**
   ```
   pip install mitmproxy
   ```

2. **Run setup script**
   ```
   start_websocket_interceptor.bat
   ```

3. **Install certificate**
   - Visit http://mitm.it
   - Install Windows certificate

4. **Configure Proxifier**
   - Route minigameapp.exe → 127.0.0.1:8080

5. **Test**
   - Open MiniWorld
   - Check room list
   - See captured messages

---

**This is the correct approach!** 🎯

WebSocket is much easier than UDP/RakNet!

Ready to start?
