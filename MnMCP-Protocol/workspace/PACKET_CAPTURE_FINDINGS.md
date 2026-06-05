# Key Findings from Packet Capture

## Critical Discovery

**MiniWorld uses TCP, not UDP for room discovery!**

From the screenshot:
- All packets are TCP
- Destination: `125.88.252.175:8081` (shequ.mini1.cn)
- Data is encrypted (TLS/SSL)
- Port 8081 is WebSocket/HTTPS

## What This Means

### Previous Assumption: ❌
- Room discovery via UDP
- RakNet protocol for rooms
- Unencrypted or AES-GCM encrypted

### Reality: ✅
- Room discovery via TCP/WebSocket
- HTTPS/TLS encryption
- Port 8081 for social/room features

## Architecture Update

```
[MiniWorld Client]
    │
    ├─ HTTP API (42.240.175.30:8080)
    │  └─ Server configuration
    │
    ├─ TCP/WebSocket (125.88.252.175:8081) ← ROOM DISCOVERY!
    │  └─ Room list
    │  └─ Room join/leave
    │  └─ Social features
    │  └─ Chat messages
    │
    └─ UDP (game servers:60023-60029)
        └─ Real-time game data (after joining room)
```

## Why Our Previous Attempts Failed

1. ❌ We intercepted HTTP API (wrong endpoint)
2. ❌ We looked for UDP (wrong protocol)
3. ❌ We didn't handle WebSocket (correct protocol!)

## New Strategy

### Option 1: WebSocket Interception

Intercept WebSocket connection to `125.88.252.175:8081`:
1. Capture WebSocket handshake
2. Monitor WebSocket frames
3. Inject fake room data
4. Forward to real server

### Option 2: TCP Proxy with TLS Interception

1. Act as man-in-the-middle
2. Intercept TLS connection
3. Decrypt traffic
4. Modify room list
5. Re-encrypt and forward

### Option 3: Hybrid Approach (Recommended)

1. **Login phase**: Passthrough to real server
   - Get session token
   - Establish WebSocket connection
   
2. **After login**: Inject into WebSocket
   - Monitor room list messages
   - Inject Minecraft room
   - Forward other messages

## Next Steps

1. **Analyze WebSocket traffic**
   - Find room list message format
   - Identify message types
   - Understand protocol

2. **Implement WebSocket proxy**
   - Intercept WebSocket connection
   - Parse messages
   - Inject fake room

3. **Test injection**
   - Add Minecraft room to list
   - Verify it appears in client

## Tools Needed

- **WebSocket proxy** (Python websockets library)
- **TLS interception** (mitmproxy or custom)
- **Message parser** (JSON or binary)

---

**The good news**: WebSocket is easier to work with than UDP!

**The challenge**: Need to handle TLS encryption

Let's implement a WebSocket interceptor next!
