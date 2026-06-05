# MnMCP v8.0 - Yeah114's Approach Analysis

## Yeah114's GitHub Projects

From github.com/Yeah114:

### Relevant Projects:

1. **FunAuth** (Go)
   - NetEase Minecraft authentication server
   - 17 stars
   - **Key**: Authentication implementation

2. **FunCore** (Go)
   - "Dynamic link library that provides connection to Chinese Minecraft"
   - **Key**: Connection bridge implementation

3. **FunShuttlerRelease**
   - Release version of FunShuttler
   - **Key**: Likely the MiniWorld-Minecraft bridge!

## Key Insight

**FunCore** description:
> "FunCore is a dynamic link library that provides a connection to the Chinese version of Minecraft and a variety of functional APIs."

**FunShuttler** likely:
- Injects into MiniWorld process
- Hooks network functions
- Redirects to Minecraft

## Yeah114's Method (Inferred)

### Approach: DLL Injection + Hook

```
[MiniWorld Process]
    │
    ├─ FunCore.dll injected
    │   │
    │   ├─ Hooks network send/receive
    │   ├─ Intercepts room creation
    │   ├─ Modifies room data
    │   └─ Redirects game traffic
    │
    └─ Connects to Minecraft instead of MiniWorld servers
```

### Technical Details

1. **DLL Injection**
   - Inject FunCore.dll into minigameapp.exe
   - Hook Winsock functions (send, recv, connect)

2. **Network Hook**
   - Intercept connect() calls
   - Redirect MiniWorld servers to local proxy
   - Modify room creation packets

3. **Protocol Translation**
   - Translate MiniWorld protocol to Minecraft
   - Handle encryption/decryption
   - Manage session state

## Implementation Options

### Option 1: DLL Injection (Yeah114's method)

**Pros**:
- ✅ Most reliable
- ✅ Bypasses all interception issues
- ✅ Works at application level

**Cons**:
- ❌ Complex to implement
- ❌ Requires reverse engineering
- ❌ May trigger anti-cheat

**Tools needed**:
- DLL injector
- API hooking library (MinHook, Detours)
- Reverse engineering skills

### Option 2: Process Monitor + Hook

Use existing tools:
- Process Hacker
- API Monitor
- Hook network APIs externally

### Option 3: Frida (Dynamic Instrumentation)

Use Frida to:
- Attach to running MiniWorld process
- Hook network functions
- Modify behavior dynamically

```javascript
// Frida script example
Interceptor.attach(Module.findExportByName("ws2_32.dll", "connect"), {
    onEnter: function(args) {
        // Modify connection target
        var sockaddr = Memory.readByteArray(args[1], 16);
        // Redirect to localhost
    }
});
```

## Recommendation

**Use Frida for rapid prototyping!**

### Why Frida?
- ✅ No need to write DLL
- ✅ Dynamic, no restart needed
- ✅ JavaScript/Python scripting
- ✅ Easy to test and modify
- ✅ Cross-platform

### Implementation Plan

1. **Install Frida**
   ```
   pip install frida frida-tools
   ```

2. **Create Frida Script**
   - Hook connect() in ws2_32.dll
   - Hook send()/recv()
   - Log and modify network traffic

3. **Attach to MiniWorld**
   ```
   frida -n minigameapp.exe -l hook_network.js
   ```

4. **Implement Bridge**
   - Redirect connections to local server
   - Translate protocols
   - Forward to Minecraft

## Next Steps

### Immediate Action

1. **Install Frida**
2. **Create basic hook script**
3. **Attach to MiniWorld**
4. **Log network calls**

### Then

5. **Identify room creation**
6. **Modify room data**
7. **Inject Minecraft room**
8. **Test connection**

---

**Let's try Frida approach! It's the fastest way to replicate Yeah114's method.**

**Do you want to install Frida and try DLL hooking?**
