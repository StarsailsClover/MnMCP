# MiniWorld Traffic Analysis Report

**Date**: 2026-04-24  
**Source**: Proxifier Logs  
**Application**: minigameapp.exe (21632)

---

## Discovered Servers

### HTTP/HTTPS Servers

| IP Address | Port | Purpose | Notes |
|------------|------|---------|-------|
| 42.240.175.30 | 8080 | Room Server | openroom.mini1.cn |
| 125.88.252.175 | 8081 | Community/Social | shequ.mini1.cn |
| 1.13.213.183 | 8080 | Game Server | |
| 1.13.213.198 | 8080 | Game Server | |
| 1.13.213.236 | 8080 | Game Server | |
| 124.70.170.213 | 8040 | Unknown | |

### UDP/Game Servers

| IP Address | Port | Purpose | Notes |
|------------|------|---------|-------|
| 117.50.185.155 | 60024 | Game Connection | |
| 129.211.227.77 | 60023 | Game Connection | |
| 14.17.92.251 | 51001 | Proxy Server | |
| 222.95.9.64 | 51003 | Proxy Server | |
| 42.224.60.227 | 62913 | Unknown | |
| 42.240.175.12 | 60029 | Punch Server | |
| 171.114.124.127 | 32183-32185 | Game Servers | Multiple ports |
| 192.168.15.177 | 60009 | Local Network | LAN game? |

### Fake IP Addresses (DNS Hijacked)

| Fake IP | Port | Real Domain |
|---------|------|-------------|
| 198.18.1.111 | 80 | Multiple domains |
| 198.18.1.113 | 80 | |
| 198.18.1.115 | 80 | |
| 198.18.1.141 | 8081 | shequ.mini1.cn |
| 198.18.1.143-146 | 8080 | Various |
| 198.18.1.147 | 443 | HTTPS |

---

## Key Findings

### 1. Connection Pattern

```
minigameapp.exe connects to:
1. HTTP API (42.240.175.30:8080) - Server config
2. Community (125.88.252.175:8081) - Social features
3. Game Servers (1.13.213.x:8080) - Multiple servers
4. UDP Servers (various:60023-60029) - Game traffic
```

### 2. Protocol Usage

- **HTTP/HTTPS**: Configuration, social features
- **TCP**: Persistent connections to game servers
- **UDP**: Real-time game traffic (likely encrypted)

### 3. Room Discovery

**Hypothesis**: Room list comes from HTTP API!

Servers involved:
- `42.240.175.30:8080` (openroom.mini1.cn)
- `1.13.213.183:8080`
- `1.13.213.198:8080`
- `1.13.213.236:8080`

### 4. Traffic Dump Files

Proxifier captured binary dumps:
- `minigameapp.exe (21632) FROM 42.240.175.30_8080 AT *.dmp`
- `minigameapp.exe (21632) FROM 125.88.252.175_8081 AT *.dmp`

These are PCAP files containing actual HTTP/TCP traffic!

---

## What This Means

### Our Proxy IS Working!

✅ **All traffic goes through proxy** (127.0.0.1:7890)
✅ **We can see all connections**
✅ **We have traffic dumps**

### But MiniWorld Still Shows Real Rooms

**Possible reasons**:

1. **Response caching**: MiniWorld cached the room list
2. **Wrong interception**: We're not modifying the right endpoint
3. **Binary protocol**: Room list might be in binary format, not JSON
4. **Multiple endpoints**: Room list comes from different server

---

## Next Steps

### 1. Analyze Traffic Dumps

The `.dmp` files contain actual HTTP traffic!

We need to:
- Extract HTTP requests/responses
- Find room list endpoint
- See actual response format

### 2. Identify Correct Endpoint

From logs, likely candidates:
- `42.240.175.30:8080` (openroom.mini1.cn)
- `1.13.213.183:8080`
- `1.13.213.198:8080`

### 3. Update Fake API

Once we know the real format:
- Match exact response structure
- Return correct data types
- Include all required fields

---

## Traffic Dump Analysis

The dump files are in PCAP format. We can analyze them with:

```python
# Read PCAP file
# Extract HTTP requests
# Parse responses
# Find room list data
```

---

## Recommendations

1. **Analyze one dump file** to see real HTTP traffic
2. **Find room list request** in the dumps
3. **Update fake API** with correct format
4. **Test again** with corrected responses

---

**The good news**: Proxifier is working perfectly!  
**The challenge**: We need to find the exact room list format.

Let's analyze the dump files next!
