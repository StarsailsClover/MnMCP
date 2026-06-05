# Logger错误修复说明

**问题**: `Cannot find module '../utils/logger'`

**原因**: 
1. logger.js 依赖 winston 模块，但未安装
2. 协议文件在独立测试时无法找到 logger

**修复方案**:

## 1. 创建备用logger实现 ✅

创建了 `logger-simple.js` - 不依赖任何外部模块的简单日志实现

## 2. 更新 logger.js ✅

修改 logger.js 自动检测 winston 是否可用：
- 如果 winston 可用，使用 winston
- 如果 winston 不可用，回退到 logger-simple

## 3. 所有引用logger的文件添加容错 ✅

修改了以下文件，添加 try-catch 容错：

### Personal端:
- `src/main/protocol/mnw-protocol.js` ✅
- `src/main/protocol/mc-protocol.js` ✅
- `src/main/protocol/protocol-translator.js` ✅
- `src/main/services/protocol-handler.js` ✅
- `src/main/services/network-capture.js` ✅
- `src/main/services/mnmcp-service.js` ✅
- `src/main/utils/config-manager.js` ✅
- `src/main/utils/logger.js` ✅

### Streamer端:
- `src/main/main.js` ✅
- `src/main/server/game-server.js` ✅

## 4. 容错代码模式

```javascript
// 尝试加载logger，如果失败则使用console
let logger;
try {
  logger = require('../utils/logger');
} catch (e) {
  logger = {
    info: (...args) => console.log('[INFO]', ...args),
    warn: (...args) => console.warn('[WARN]', ...args),
    error: (...args) => console.error('[ERROR]', ...args),
    debug: (...args) => {},
  };
}
```

## 5. 现在可以运行了

### 安装依赖后运行:
```bash
cd MnMCP-Personal
npm install
run.bat
```

或者如果不安装依赖，logger会自动回退到console输出。

## 6. 建议

首次运行前建议执行:
```bash
npm install
```

这会安装 winston 等依赖，获得完整的日志功能。
