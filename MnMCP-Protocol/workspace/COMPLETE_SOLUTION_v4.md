# MnMCP v4.0 - Complete Solution with Proxifier

**Based on full protocol understanding from documentation**

---

## What We Now Know

### MiniWorld Protocol Stack

```
[Application Layer]
├─ HTTP API (openroom.mini1.cn:8080)
│  └─ Server configuration ONLY
│      GET /server/room?cmd=server_config
│      Response: {"config": {...}, "result": 0}
│
├─ UDP Protocol (RakNet based)
│  ├─ Room discovery
│  ├─ Heartbeat
│  └─ Non-sensitive status
│  └─ Encryption: AES-128-GCM + ECDH + HKDF
│
└─ WebSocket/SSL
   └─ Core game logic (battle, resources, commands)
```

### Why Previous Approach Failed

1. ❌ Tried to fake HTTP room list (doesn't exist!)
2. ❌ Only intercepted HTTP (rooms use UDP!)
3. ❌ Wrong response format
4. ❌ Didn't handle encryption

---

## New Strategy: Full Traffic Capture

### Step 1: Use Proxifier

**Purpose**: Capture ALL MiniWorld traffic (HTTP/UDP/TCP)

**Setup**:
1. Import profile: `MnMCP_Proxifier_Profile.ppx`
2. Route miniworld.exe through proxy (127.0.0.1:7890)
3. Enable logging

**What we'll see**:
- All HTTP requests
- All UDP packets (encrypted)
- All TCP connections
- Destination IPs and ports

### Step 2: Analyze Traffic

**Look for**:
- UDP packets to specific ports
- Room discovery protocol
- Encrypted packet structure
- Server IPs

### Step 3: Implement UDP Interception

**Using WinDivert**:
```python
# Capture UDP packets
# Decrypt using AES-128-GCM
# Modify room data
# Re-encrypt
# Forward
```

---

## Current Status

### Ready to Use

✅ **Proxifier Profile**: `MnMCP_Proxifier_Profile.ppx`
✅ **Proxy Server**: Running on 127.0.0.1:7890
✅ **Fake API**: Running on 127.0.0.1:8080
✅ **Crypto Implementation**: Available in resources
✅ **UDP Decoder**: Available in resources

### Next Actions

1. **Import Proxifier profile**
2. **Start MiniWorld**
3. **Capture traffic**
4. **Analyze UDP packets**
5. **Implement interception**

---

## How to Test

### 1. Import Proxifier Profile

```
File -> Import Profile -> MnMCP_Proxifier_Profile.ppx
```

Or manually:
1. Profile -> Proxy Servers -> Add
   - Address: 127.0.0.1
   - Port: 7890
   - Protocol: HTTP

2. Profile -> Proxification Rules -> Add
   - Name: MiniWorld
   - Applications: miniworld.exe
   - Target hosts: Any
   - Target ports: Any
   - Action: Proxy HTTP 127.0.0.1

### 2. Enable Logging

```
Profile -> Advanced -> Log Settings
- Enable: Log all connections
- Log file: proxifier_log.txt
```

### 3. Start MiniWorld

1. Open MiniWorld
2. Go to "Online" menu
3. Watch Proxifier log

### 4. Analyze Log

Look for:
```
[UDP] miniworld.exe -> 42.240.175.30:xxxxx
[UDP] miniworld.exe -> 129.211.227.176:xxxxx
[TCP] miniworld.exe -> openroom.mini1.cn:8080
```

---

## Expected Traffic Pattern

### Initial Connection

```
1. HTTP -> openroom.mini1.cn:8080
   GET /server/room?cmd=server_config
   Response: Server IP and ports

2. UDP -> <server_ip>:<udp_port>
   Encrypted RakNet packets
   Room discovery / Join room

3. WebSocket/SSL -> <server_ip>:<ws_port>
   Game data synchronization
```

### Room List Request

**Hypothesis**: Room list is fetched via UDP, not HTTP!

```
UDP Packet Structure:
[RakNet Header]
[Encrypted Payload]
  └─ Decrypted: Room list request
     Response: List of available rooms
```

---

## Implementation Plan

### Phase 1: Traffic Analysis (Current)

- [x] Generate Proxifier profile
- [ ] Import profile
- [ ] Capture MiniWorld traffic
- [ ] Identify room discovery protocol
- [ ] Document packet structure

### Phase 2: UDP Interception

- [ ] Install WinDivert
- [ ] Implement packet capture
- [ ] Decrypt packets (AES-128-GCM)
- [ ] Parse room data
- [ ] Inject Minecraft room

### Phase 3: Integration

- [ ] Connect to Minecraft LAN
- [ ] Translate protocols
- [ ] Test end-to-end

---

## Files Created

```
workspace/
├── MnMCP_Proxifier_Profile.ppx      <- Import this
├── generate_proxifier_profile.py    <- Generator script
├── mnmcp_proxy.py                   <- HTTP/HTTPS proxy
├── mnmcp_fake_api.py                <- Fake API server
└── PROTOCOL_UNDERSTANDING_v4.md     <- This document
```

---

## Next Step

**Import the Proxifier profile and start capturing traffic!**

```desktop-local-file
{
  "localPath": "D:\\Coding\\BlockConnect\\BlockConnect-MnMCP\\workspace\\MnMCP_Proxifier_Profile.ppx",
  "fileName": "MnMCP_Proxifier_Profile.ppx"
}
```

Then:
1. Open Proxifier
2. File -> Import Profile
3. Select this file
4. Start MiniWorld
5. Tell me what you see in the log!

---

**We're on the right track now!** 🚀
