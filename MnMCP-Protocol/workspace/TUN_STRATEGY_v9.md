# MnMCP v9.0 - TUN Mode with Full Traffic Capture

Based on security analysis, avoiding Frida (anti-Frida measures detected)

## Security Analysis Summary

From SO analysis:
- ✅ **libInnoSecure.so** - Anti-debug/injection
- ✅ **libsgcore.so** - Tencent security core
- ✅ **libqmcheat.so** - Cheat detection
- ✅ **Anti-Frida measures present**

**Decision**: Use TUN mode for traffic capture (bypasses app-level security)

---

## Strategy: TUN + Traffic Analysis

### Architecture

```
[MiniWorld App]
    │
    ▼ (All traffic forced through TUN)
[Clash Meta TUN Interface]
    │
    ├─ Intercepts ALL network traffic
    ├─ Logs every packet
    ├─ Forwards to real servers (passthrough)
    │
    ▼
[MiniWorld Servers]
```

### Phase 1: Pure Logging (Current)

1. **Enable TUN mode**
2. **Log all traffic** (no modification)
3. **Analyze protocol** from logs
4. **Identify room list endpoint**

### Phase 2: Selective Modification

1. **Identify specific requests** to modify
2. **Implement packet modification**
3. **Inject Minecraft room**

---

## Implementation

### Step 1: TUN Configuration

```yaml
# Full capture mode
tun:
  enable: true
  stack: system
  dns-hijack:
    - 8.8.8.8:53
  auto-route: true
  auto-detect-interface: true

# Log everything
log-level: debug

# Rules: Allow all, log all
rules:
  - MATCH,DIRECT
```

### Step 2: Traffic Logger

```python
# Log all packets for analysis
class TrafficLogger:
    def log_packet(self, src, dst, data):
        # Save to pcap or text
        # Analyze protocol
        pass
```

### Step 3: Protocol Analysis

From captured traffic:
1. Identify HTTP/WebSocket endpoints
2. Decode encryption (if possible)
3. Find room list request/response

---

## Key Findings from SO Analysis

### Network Stack

From liblibGameApp.so:
- **libilink_network.so** - Network communication
- **libcurl** - HTTP client
- **WebSocket** support

### Login System

Key functions:
- `OnLoginResult` @ 0x2ec81a4
- `SetTpLoginAccount` @ 0x2ec8084
- `nativeGetMiniToken` @ 0x2ec5684

### Security Layers

```
Layer 5: App logic
Layer 4: Anti-cheat (libqmcheat.so)
Layer 3: Security (libInnoSecure.so)
Layer 2: Encryption (libEncryptor.so)
Layer 1: Loader (libMiniTechLoader.so)
```

---

## Next Steps

### Immediate

1. **Start TUN mode with full logging**
2. **Open MiniWorld**
3. **Login and navigate to room list**
4. **Capture all traffic**
5. **Analyze logs**

### Analysis

From logs, identify:
- Room list endpoint
- Request format
- Response format
- Encryption method

### Then

Implement modification based on captured protocol.

---

**Let's start with pure TUN logging!**
