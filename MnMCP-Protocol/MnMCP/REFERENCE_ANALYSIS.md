# 参考版本分析 - v 3.26.0.0_dev Phase 6-20260530 (1145)

**分析时间**: 2026-05-23  
**来源**: 组员提供的参考实现  
**状态**: 已有可用版本，需开发原生实现

---

## 🎯 关键信息提取

### 启动参数

```bash
# 1. 启动后端
python backend.py

# 2. 启动代理
.\raknet_proxy\build\release\mn2mc_proxy.exe \
  --mode dual \
  --port 19132 \
  --host-port 19133 \
  --guid 598340631 \
  --lan-ip 192.168.1.7 \
  --backend 127.0.0.1:19134
```

### 端口架构

```
┌─────────────────────────────────────────────┐
│            端口使用架构                       │
├─────────────────────────────────────────────┤
│                                              │
│  ┌─────────────┐     ┌─────────────┐      │
│  │ 迷你世界客户端 │ ←→ │  :19132      │      │
│  │             │     │ (对外端口1)   │      │
│  └─────────────┘     └──────┬──────┘      │
│                              │              │
│  ┌─────────────┐     ┌──────┴──────┐       │
│  │ Minecraft   │ ←→ │  :19133      │       │
│  │ 客户端      │     │ (对外端口2)   │       │
│  └─────────────┘     └──────┬──────┘       │
│                              │              │
│  ┌─────────────┐     ┌──────┴──────┐       │
│  │ mn2mc_proxy │ ←→ │  :19134      │       │
│  │  (Rust/C++) │     │ (后端端口)   │       │
│  └─────────────┘     └─────────────┘       │
│                              │              │
│  ┌─────────────┐     ┌──────┴──────┐       │
│  │ 后端服务     │ ←→ │  backend    │       │
│  │ (Python)    │     │             │       │
│  └─────────────┘     └─────────────┘       │
│                                              │
└─────────────────────────────────────────────┘

端口说明:
- 19132: 迷你世界客户端连接端口 (对外)
- 19133: Minecraft客户端连接端口 (对外)  
- 19134: 后端服务端口 (内部)
```

---

## 🔧 技术架构分析

### 组件拆分

| 组件 | 语言 | 功能 | 位置 |
|------|------|------|------|
| mn2mc_proxy.exe | Rust/C++ | 核心代理，协议转换 | `raknet_proxy/build/release/` |
| backend.py | Python | 后端服务，地图处理 | 根目录 |
| 本地存档 | - | 地图数据 | 需修改路径 |

### 关键参数

```
--mode dual          # 双模式：同时支持迷你世界和MC
--port 19132         # 迷你世界监听端口
--host-port 19133    # Minecraft监听端口
--guid 598340631     # 迷你世界用户ID
--lan-ip 192.168.1.7 # 本机局域网IP（返回给客户端）
--backend 127.0.0.1:19134  # 后端服务地址
```

### Dual模式理解

```
Dual模式 = 同时运行两种协议
├── 迷你世界协议 (RakNet) → 端口19132
└── Minecraft协议 (TCP)  → 端口19133

数据流向:
迷你世界客户端 → 19132 → mn2mc_proxy → 19134 → backend.py
Minecraft客户端 → 19133 → mn2mc_proxy → 19134 → backend.py

协议转换在mn2mc_proxy中完成
```

---

## 📦 关键修改点

### 1. 地图路径修改

**当前**: 使用本地存档（临时）  
**需要**: 修改为生产环境路径

```python
# backend.py 中
MAP_PATH = "./worlds/default"  # ← 修改这里
```

### 2. 返回IP字段修改

**当前**: 返回局域网IP  
**问题**: 不同网络环境需要不同IP

```
当前实现:
- 返回 192.168.1.7 (固定)

需要改进:
- 自动检测本机IP
- 支持配置
- 支持公网/内网切换
```

### 3. 材质提取

```bash
# 使用解包器提取材质
python pkg_unpacker.py --decode-texture --input miniworld.pkg
```

---

## 🏗️ 我们的原生实现计划

### 架构对比

| 组件 | 参考版本 | 我们的实现 |
|------|----------|-----------|
| 核心代理 | Rust/C++ (mn2mc_proxy.exe) | **Python** (原生) |
| 后端服务 | Python (backend.py) | **Python** (集成) |
| 地图处理 | 本地存档 | **动态生成/加载** |
| 协议支持 | dual模式 | **dual + passthrough** |

### 原生实现优势

1. **纯Python** - 易于修改和调试
2. **模块化** - 清晰的架构分层
3. **配置灵活** - 通过config.yaml
4. **扩展性强** - 易于添加新功能

---

## 📝 Phase 6 开发计划

### Phase 6: 参考版本移植与优化

#### 任务6.1: 端口架构实现

```python
# mn2mc/server/dual_server.py

class DualServer:
    """
    三端口架构:
    - port: 迷你世界客户端端口
    - host_port: Minecraft客户端端口
    - backend_port: 后端服务端口
    """
    
    def __init__(self, config):
        self.mini_port = config.get('mini_port', 19132)
        self.mc_port = config.get('mc_port', 19133)
        self.backend_port = config.get('backend_port', 19134)
        self.lan_ip = config.get('lan_ip', '192.168.1.7')
        self.guid = config.get('guid', 0)
```

#### 任务6.2: 后端服务集成

```python
# mn2mc/backend/world_service.py

class WorldService:
    """地图服务"""
    
    def __init__(self, map_path):
        self.map_path = map_path
        self.world = self.load_world()
    
    def load_world(self):
        """加载本地存档"""
        # 支持迷你世界存档格式
        pass
    
    def get_chunk(self, x, z):
        """获取区块数据"""
        pass
```

#### 任务6.3: IP自动检测

```python
# mn2mc/utils/network.py

def get_lan_ip():
    """自动获取局域网IP"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"
```

#### 任务6.4: 材质提取集成

```python
# mn2mc/utils/texture_extractor.py

class TextureExtractor:
    """材质提取器"""
    
    def extract_from_pkg(self, pkg_path):
        """从pkg文件提取材质"""
        import subprocess
        subprocess.run([
            'python', 'pkg_unpacker.py',
            '--decode-texture',
            '--input', pkg_path,
            '--output', './textures/'
        ])
```

---

## 🚀 立即执行

### 今天 (2026-05-23)

1. **创建DualServer架构**
   - 三端口实现
   - 模式切换

2. **集成后端服务**
   - 地图加载
   - 区块处理

3. **添加IP自动检测**
   - 局域网IP获取
   - 公网IP支持

### 明天 (2026-05-24)

4. **材质提取集成**
   - 调用pkg_unpacker
   - 纹理处理

5. **测试验证**
   - 三端口通信
   - 双客户端连接

---

## 📊 预期成果

| 功能 | 参考版本 | 我们的实现 | 状态 |
|------|----------|-----------|------|
| 三端口 | ✅ | 开发中 | 🔄 |
| Dual模式 | ✅ | 开发中 | 🔄 |
| 地图加载 | ✅ (本地存档) | 动态加载 | 🔄 |
| IP返回 | ✅ (固定) | 自动检测 | 🔄 |
| 材质提取 | ✅ (手动) | 集成调用 | 🔄 |

---

## 💡 关键改进点

### 1. 配置化

```yaml
# config.yaml
server:
  mode: dual  # dual, mini, mc
  mini_port: 19132
  mc_port: 19133
  backend_port: 19134
  lan_ip: auto  # auto detect
  
backend:
  map_path: ./worlds/default
  texture_path: ./textures/
```

### 2. 自动IP检测

```python
# 自动检测并配置
if config['lan_ip'] == 'auto':
    config['lan_ip'] = get_lan_ip()
```

### 3. 地图路径配置

```python
# 支持多种地图源
MAP_SOURCES = {
    'local': './worlds/default',
    'miniworld': './miniworld_saves/',
    'minecraft': './minecraft_saves/'
}
```

---

## ✅ 检查清单

Phase 6 完成标准:

- [ ] DualServer三端口实现
- [ ] 后端服务集成
- [ ] 地图加载 (配置化路径)
- [ ] IP自动检测
- [ ] 材质提取集成
- [ ] 启动脚本 (模拟参考版本)
- [ ] 文档更新

---

**基于参考版本，开发原生Python实现！**
