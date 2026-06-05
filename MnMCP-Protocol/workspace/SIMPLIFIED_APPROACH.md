# MnMCP - Simplified Direct Connection Approach

## Problem Summary

- Intercepting MiniWorld traffic is very complex
- TUN mode, hosts file, Proxifier all have issues
- MiniWorld might use hardcoded connections

## Simplified Solution

**Skip interception entirely!**

Instead of intercepting MiniWorld's traffic, we:

1. ✅ **Start Minecraft LAN** (already done)
2. ✅ **Create a simple bridge** that listens on a port
3. ⏳ **Manually configure MiniWorld** to connect to our bridge
4. ⏳ **Translate protocols** between MiniWorld and Minecraft

## How It Works

```
[Minecraft Java] (already running)
    │
    └─ LAN on port 54321 (example)
    
[MnMCP Bridge] (we create this)
    │
    ├─ Listens on port 19132 (MiniWorld default)
    ├─ Accepts MiniWorld connections
    ├─ Translates MiniWorld protocol to Minecraft
    └─ Forwards to Minecraft LAN

[MiniWorld Client]
    │
    └─ Connects to 127.0.0.1:19132 (our bridge)
```

## Implementation

### Step 1: Get Minecraft LAN Info

From your earlier test:
- Minecraft LAN port: `54321` (or check current)
- IP: `127.0.0.1`

### Step 2: Start Bridge

Run bridge that:
1. Listens on `0.0.0.0:19132`
2. Accepts MiniWorld protocol
3. Connects to Minecraft at `127.0.0.1:54321`
4. Translates between protocols

### Step 3: Connect MiniWorld

In MiniWorld:
1. Go to "联机" (Online)
2. Select "加入房间" (Join Room)
3. Enter: `127.0.0.1:19132`
4. Click connect

## Advantages

- ✅ No interception needed
- ✅ No TUN mode
- ✅ No hosts file
- ✅ No certificate issues
- ✅ Direct and simple

## Challenges

- ⚠️ Need to implement MiniWorld protocol
- ⚠️ Need protocol translation
- ⚠️ MiniWorld might not allow manual IP entry

## Let's Try!

Should we implement the simplified bridge approach?

This is much more reliable than interception!
