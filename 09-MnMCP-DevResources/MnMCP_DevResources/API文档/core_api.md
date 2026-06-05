# MnMCP Core API 文档

## ProxyServerV2

### 类定义
```python
from core.proxy_server_v2 import ProxyServerV2, ProxyConfig

class ProxyServerV2:
    def __init__(self, config: ProxyConfig)
    async def start(self)
    async def stop(self)
    def get_stats(self) -> Dict
```

### 配置
```python
@dataclass
class ProxyConfig:
    mnw_host: str = "0.0.0.0"
    mnw_port: int = 8080
    mc_host: str = "127.0.0.1"
    mc_port: int = 19132
    max_clients: int = 100
```

### 使用示例
```python
import asyncio
from core.proxy_server_v2 import ProxyServerV2, ProxyConfig

async def main():
    config = ProxyConfig(
        mnw_port=8080,
        mc_port=19132
    )
    server = ProxyServerV2(config)
    await server.start()

asyncio.run(main())
```

---

## BlockMapper

### 类定义
```python
from protocol.block_mapper import BlockMapper

class BlockMapper:
    def __init__(self, mapping_file: str = None)
    def mc_to_mnw_block(self, mc_id: int, mc_meta: int = 0) -> Tuple[int, int]
    def mnw_to_mc_block(self, mnw_id: int, mnw_meta: int = 0) -> Tuple[int, int]
```

### 使用示例
```python
mapper = BlockMapper()

# MC to MNW
mnw_id, mnw_meta = mapper.mc_to_mnw_block(1, 0)  # stone

# MNW to MC
mc_id, mc_meta = mapper.mnw_to_mc_block(1, 0)
```

---

## PacketTranslator

### 类定义
```python
from protocol.packet_translator import PacketTranslator

class PacketTranslator:
    def __init__(self, block_mapper: BlockMapper = None)
    def translate_mnw_to_mc(self, mnw_packet: Packet) -> Packet
    def translate_mc_to_mnw(self, mc_packet: Packet) -> Packet
```

---

## PerformanceMonitor

### 类定义
```python
from utils.performance_monitor import PerformanceMonitor

class PerformanceMonitor:
    def record_packet(self, packet_size: int, latency_ms: float)
    def record_metrics(self, latency_ms: float, memory_mb: float, cpu_percent: float)
    def get_statistics(self, window_size: int = 100) -> Dict
```

### 使用示例
```python
monitor = PerformanceMonitor()
monitor.record_packet(100, 10.5)
stats = monitor.get_statistics()
```

---

## ErrorHandler

### 类定义
```python
from utils.error_handler import ErrorHandler, ErrorContext

class ErrorHandler:
    def handle(self, error: Exception, context: dict = None) -> ErrorContext
    def on_alert(self, callback: Callable[[ErrorContext], None])
    def get_error_stats(self) -> dict
```
