# MnMCP v4.0 - Complete Protocol Understanding

## Critical Findings from Documentation

### 1. MiniWorld Network Architecture

**Mixed Protocol System**:
- **UDP Protocol**: For heartbeat, non-sensitive status (RakNet based)
- **WebSocket/SSL**: For core game logic (battle, resources, commands)
- **HTTP API**: For server configuration only (not room list!)

### 2. UDP Packet Structure (RakNet)

```
Offset  Len  Field
0       2    Magic/Version
2       2    CmdID
4       4    SeqNo
8       4    BodyLen
12      1    EncryptAlgo (0=HybridEcdh, 1=AesGcm)
13      1    CompressAlgo (0=none, 1/4=zlib, 2=lz4)
14      1    CompressVersion
15      1    HeaderEnd/Flags
16      12   Nonce (GCM IV, 96-bit)
28      N    Ciphertext
28+N    16   GCM Tag
```

### 3. Encryption Chain

**Key Derivation**:
1. ECDH handshake → shared_secret (32B)
2. HKDF_Extract(salt=0, IKM=shared_secret) → PRK
3. HKDF_Expand(..., length=48) → session material
4. Split: aes_key[0:16], nonce_base[16:28]

**Encryption**: AES-128-GCM (NOT AES-CBC!)

### 4. HTTP API (openroom.mini1.cn:8080)

**NOT for room list!** Only for server configuration:

**Request**:
```
GET /server/room?cmd=server_config&uin=<uid>&auth=<signature>
```

**Response**:
```json
{
  "config": {
    "room": {
      "ip": "129.211.227.176",
      "port": 8080
    },
    "proxy": {
      "ip": "49.65.156.87",
      "port": 51001
    },
    "punch": {
      "ip": "1.13.213.223",
      "port": 60021
    },
    "network_type": 1,
    "room_name": "hd_room_ct-5001"
  },
  "result": 0
}
```

### 5. Real Room Discovery

**MiniWorld uses UDP/TCP for room discovery, NOT HTTP!**

Possible mechanisms:
1. **UDP Broadcast**: Like Minecraft LAN discovery
2. **Central Server UDP**: Query room list via UDP
3. **P2P Discovery**: Direct peer discovery

### 6. Why Our Approach Failed

1. ❌ Wrong API format (used `ret` instead of `result`)
2. ❌ Wrong endpoint (tried to fake room list, but it doesn't exist in HTTP)
3. ❌ Only intercepted HTTP, but MiniWorld uses UDP/TCP for rooms
4. ❌ Didn't handle encryption (AES-128-GCM)

## New Strategy

### Option 1: UDP Interception (Recommended)

Intercept UDP traffic to/from MiniWorld servers:
- Capture UDP packets
- Decrypt using AES-128-GCM
- Modify room data
- Re-encrypt and forward

**Tools needed**:
- WinDivert or Npcap for packet capture
- Python cryptography for AES-GCM
- ECDH keys from resources

### Option 2: Proxifier + Full Protocol Implementation

Use Proxifier to route ALL traffic through our proxy:
- Handle UDP/TCP/HTTP
- Implement RakNet protocol
- Decrypt/encrypt packets
- Inject fake Minecraft room

### Option 3: Local Server Emulation

Create a complete MiniWorld server emulator:
- Listen on UDP port
- Implement RakNet protocol
- Handle encryption
- Present as a room that connects to Minecraft

## Resources Available

From your files:
- ✅ Complete crypto implementation (AES-GCM, ECDH, HKDF)
- ✅ UDP packet decoder (RakNet)
- ✅ Encryption keys and algorithms
- ✅ Protocol specifications
- ✅ Captured traffic samples

## Next Steps

1. **Use Proxifier** to capture ALL MiniWorld traffic
2. **Analyze UDP packets** to find room discovery protocol
3. **Implement UDP interception** with WinDivert
4. **Decrypt packets** using AES-128-GCM
5. **Inject Minecraft room** into room list

---

**This is a complete rewrite of our approach!**
