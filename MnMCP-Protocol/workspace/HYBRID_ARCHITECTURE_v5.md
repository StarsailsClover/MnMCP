# MnMCP v5.0 - Hybrid Architecture Design

**Concept**: Seamless switching between real server and emulated server

---

## Architecture Overview

```
[MiniWorld Client]
    │
    ▼
[MnMCP Proxy Layer] ← Intercepts ALL traffic
    │
    ├─ Mode 1: Passthrough (Login)
    │   └─ Forward to real servers
    │       ├─ Authentication
    │       ├─ Player data sync
    │       └─ Get session token
    │
    └─ Mode 2: Emulation (Gaming)
        └─ Local RakNet server
            ├─ Fake room list (with Minecraft room)
            ├─ Bridge to Minecraft
            └─ Protocol translation
```

---

## Switching Mechanism

### Method 1: Login Hijack (Recommended)

```
1. [Client] → Login request → [Proxy] → [Real Server]
2. [Real Server] → Login success → [Proxy]
3. [Proxy] Intercepts response, extracts:
   - Session token
   - User ID
   - Player data
4. [Proxy] → Modified response → [Client]
5. [Proxy] Switches to emulation mode
6. [Client] Requests room list → [Proxy] Returns fake list
```

**Advantages**:
- ✅ Real authentication
- ✅ Valid session
- ✅ Player data synced
- ✅ Seamless transition

### Method 2: Command-based Switch

```
User types command in chat:
- "/mnmcp real" → Switch to real server
- "/mnmcp fake" → Switch to emulated server
- "/mnmcp minecraft" → Show Minecraft rooms
```

**Advantages**:
- ✅ User control
- ✅ Can switch anytime
- ✅ No restart needed

---

## Implementation Design

### Component 1: Smart Proxy

```python
class MnMCPSmartProxy:
    """Smart proxy with mode switching"""
    
    def __init__(self):
        self.mode = "passthrough"  # or "emulation"
        self.session_data = {}
        self.user_id = None
        
    def handle_request(self, request):
        if self.mode == "passthrough":
            return self.forward_to_real_server(request)
        else:
            return self.handle_locally(request)
    
    def on_login_success(self, response):
        """Called when login succeeds"""
        # Extract session data
        self.session_data = extract_session(response)
        self.user_id = response['uid']
        
        # Auto-switch to emulation mode
        if AUTO_SWITCH_ENABLED:
            self.mode = "emulation"
            logger.info("Switched to emulation mode")
    
    def switch_mode(self, new_mode):
        """Manually switch mode"""
        self.mode = new_mode
        logger.info(f"Mode switched to: {new_mode}")
```

### Component 2: Session Manager

```python
class SessionManager:
    """Manage MiniWorld session"""
    
    def __init__(self):
        self.token = None
        self.uid = None
        self.player_data = {}
        self.encryption_keys = {}
    
    def capture_from_login(self, response):
        """Capture session from login response"""
        self.token = response.get('token')
        self.uid = response.get('uid')
        self.player_data = response.get('player_data', {})
        
        # Extract encryption keys if present
        if 'ecdh_public_key' in response:
            self.derive_encryption_keys(response)
    
    def derive_encryption_keys(self, handshake_data):
        """Derive AES-GCM keys from ECDH"""
        # Use ECDH + HKDF from resources
        shared_secret = ecdh_compute(handshake_data)
        self.encryption_keys = hkdf_derive(shared_secret)
```

### Component 3: Local RakNet Server

```python
class LocalRakNetServer:
    """Emulated MiniWorld server"""
    
    def __init__(self, session_manager):
        self.session = session_manager
        self.rooms = []
        self.minecraft_rooms = []
        
    async def start(self, port=19132):
        """Start UDP server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', port))
        
        while True:
            data, addr = await self.sock.recvfrom(4096)
            await self.handle_packet(data, addr)
    
    async def handle_packet(self, data, addr):
        """Handle RakNet packet"""
        # Decrypt
        decrypted = self.decrypt_packet(data)
        
        # Parse
        packet = parse_raknet_packet(decrypted)
        
        # Handle based on type
        if packet.type == ROOM_LIST_REQUEST:
            await self.send_room_list(addr)
        elif packet.type == JOIN_ROOM:
            await self.handle_join_room(packet, addr)
    
    async def send_room_list(self, addr):
        """Send fake room list with Minecraft room"""
        rooms = [
            {
                "room_id": "999999999",
                "room_name": "🎮 Minecraft Server",
                "players": 1,
                "max_players": 20,
                "map_id": self.minecraft_map_id
            }
        ]
        
        # Add real rooms if in hybrid mode
        if SHOW_REAL_ROOMS:
            rooms.extend(self.fetch_real_rooms())
        
        response = build_room_list_packet(rooms)
        encrypted = self.encrypt_packet(response)
        self.sock.sendto(encrypted, addr)
```

### Component 4: Mode Switcher

```python
class ModeSwitcher:
    """Handle mode switching"""
    
    def __init__(self, proxy, server):
        self.proxy = proxy
        self.server = server
        self.hotkey_enabled = True
        
    def enable_chat_commands(self):
        """Monitor chat for commands"""
        # Intercept chat packets
        self.proxy.add_packet_handler(CHAT_MESSAGE, self.on_chat)
    
    def on_chat(self, packet):
        """Handle chat commands"""
        message = packet.get('message', '')
        
        if message.startswith('/mnmcp'):
            args = message.split()
            
            if len(args) < 2:
                return self.show_help()
            
            command = args[1]
            
            if command == 'real':
                self.switch_to_real()
            elif command == 'fake':
                self.switch_to_fake()
            elif command == 'minecraft':
                self.toggle_minecraft_rooms()
            elif command == 'status':
                self.show_status()
    
    def switch_to_real(self):
        """Switch to real server"""
        self.proxy.mode = "passthrough"
        self.send_notification("Switched to real server")
    
    def switch_to_fake(self):
        """Switch to emulated server"""
        self.proxy.mode = "emulation"
        self.send_notification("Switched to emulated server")
    
    def send_notification(self, message):
        """Send in-game notification"""
        # Inject chat message packet
        packet = build_chat_packet(f"[MnMCP] {message}")
        self.proxy.inject_packet(packet)
```

---

## Traffic Flow

### Scenario 1: Login Phase

```
1. Client → Login request
   ↓
2. Proxy (passthrough mode)
   ↓
3. Real server → Login success
   ↓
4. Proxy intercepts:
   - Saves session token
   - Saves encryption keys
   - Saves player data
   ↓
5. Proxy → Forward to client
   ↓
6. [AUTO SWITCH] Proxy switches to emulation mode
```

### Scenario 2: Room List Request

```
Mode: Emulation

1. Client → Room list request (UDP)
   ↓
2. Proxy intercepts
   ↓
3. Local RakNet server handles:
   - Decrypts packet
   - Generates fake room list
   - Includes Minecraft room
   - Encrypts response
   ↓
4. Proxy → Response to client
   ↓
5. Client shows rooms (including Minecraft!)
```

### Scenario 3: User Switches Back

```
User types: /mnmcp real

1. Proxy intercepts chat
   ↓
2. Detects command
   ↓
3. Switches mode to passthrough
   ↓
4. Sends notification
   ↓
5. Next request → Forwarded to real server
```

---

## Configuration

```yaml
# mnmcp_config.yaml

proxy:
  port: 7890
  mode: auto  # auto, passthrough, emulation
  
auto_switch:
  enabled: true
  trigger: login_success  # login_success, manual, never
  
emulation:
  udp_port: 19132
  show_real_rooms: false
  inject_minecraft_room: true
  
minecraft:
  lan_discovery: true
  room_name: "🎮 Minecraft Server"
  
commands:
  enabled: true
  prefix: "/mnmcp"
  
notifications:
  enabled: true
  show_mode_switch: true
```

---

## User Experience

### Startup

```
1. User starts MnMCP
2. User starts MiniWorld
3. User logs in normally
4. [MnMCP] Login successful! Session captured.
5. [MnMCP] Switched to emulation mode.
6. User sees room list with Minecraft room!
```

### Switching

```
User types: /mnmcp real
[MnMCP] Switched to real server
[MnMCP] You will see real rooms now

User types: /mnmcp fake
[MnMCP] Switched to emulated server
[MnMCP] Minecraft room is now visible
```

### Status Check

```
User types: /mnmcp status
[MnMCP] Status:
  Mode: emulation
  Session: Active (UID: 2056574316)
  Minecraft: Discovered (192.168.1.7:54056)
  Real server: Connected
```

---

## Implementation Priority

### Phase 1: Basic Proxy (2-3 hours)
- [x] HTTP/HTTPS proxy
- [ ] UDP packet capture
- [ ] Session extraction
- [ ] Mode switching

### Phase 2: RakNet Server (4-6 hours)
- [ ] UDP server
- [ ] Packet encryption/decryption
- [ ] Room list generation
- [ ] Minecraft room injection

### Phase 3: Mode Switching (2-3 hours)
- [ ] Chat command parser
- [ ] Auto-switch on login
- [ ] Manual switch commands
- [ ] Status notifications

### Phase 4: Minecraft Bridge (4-6 hours)
- [ ] Connect to Minecraft LAN
- [ ] Protocol translation
- [ ] Data forwarding

**Total**: 12-18 hours

---

## Next Steps

1. **Implement UDP packet capture** (WinDivert)
2. **Extract session from login**
3. **Create local RakNet server**
4. **Test room list injection**
5. **Add mode switching**

---

**This is the best approach!** 🎯

Advantages:
- ✅ Real authentication
- ✅ Seamless switching
- ✅ No restart needed
- ✅ User control
- ✅ Can fall back to real server anytime

Shall we start implementing?
