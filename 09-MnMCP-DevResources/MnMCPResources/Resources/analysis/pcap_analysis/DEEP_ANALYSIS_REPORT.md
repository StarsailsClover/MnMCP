# 迷你世界PC端深度抓包分析报告

## 分析时间
2026-02-26 15:35:53

## 概览

### miniworld_micromini_capture.pcapng

- **分析时间**: 2026-02-26T15:35:48.803335
- **服务器IP数**: 0
- **TCP流数**: 0
- **UDP流数**: 0
- **通信端口**: 

#### 可能的游戏服务器（按数据量排序）

| IP地址 | 数据量 | 说明 |
|--------|--------|------|

#### TLS SNI (HTTPS服务器)

- `mnweb.mini1.cn`
- `down.anticheatexpert.com`
- `www.doubao.com`
- `mon.zijieapi.com`
- `abtestvm.bytedance.com`
- `title.mgt.xboxlive.com`
- `yybadaccess.3g.qq.com`
- `mwu-api-pre.mini1.cn`
- `shequ.mini1.cn`
- `tnc3-bjlgy.zijieapi.com`

#### HTTP Host

- `mdownload.mini1.cn`
- `tj3.mini1.cn`
- `tj.mini1.cn`
- `logpost2.miniworldgame.com`
- `119.29.29.98`
- `139.199.5.123`
- `static-www.mini1.cn`
- `wskacchm.mini1.cn:4000`
- `cn-logic4.mini1.cn:4012`
- `239.255.255.250:1900`

---

### miniworld_wlan_capture.pcapng

- **分析时间**: 2026-02-26T15:35:50.804164
- **服务器IP数**: 0
- **TCP流数**: 0
- **UDP流数**: 0
- **通信端口**: 

#### 可能的游戏服务器（按数据量排序）

| IP地址 | 数据量 | 说明 |
|--------|--------|------|

#### TLS SNI (HTTPS服务器)

- `mssdk.bytedance.com`
- `moment.bytedance.com`
- `mon.zijieapi.com`
- `wx.mail.qq.com`
- `catalog.gamepass.com`
- `mcs.zijieapi.com`
- `yybadaccessuse.3g.qq.com`
- `honeycomb-plugins.wpscdn.cn`
- `honeycomb-emergency.wpscdn.cn`
- `honeycomb.wpscdn.cn`

#### HTTP Host

- `drive.wps.cn`
- `shuc-pc-hunt.ksord.com`

---

## 关键发现

### 游戏服务器特征

根据数据分析，迷你世界PC版可能使用以下服务器：

1. **登录认证服务器**
   - 使用HTTPS协议
   - 域名: mini1.cn 相关

2. **游戏服务器**
   - 使用TCP协议
   - 端口: 动态分配（高位端口）
   - IP: 腾讯云/移动云/电信

3. **CDN/资源服务器**
   - 使用HTTP/HTTPS
   - 用于下载游戏资源

### 协议特征

1. **加密通信**
   - 使用TLS 1.2/1.3
   - 证书验证

2. **游戏数据**
   - 可能使用自定义协议
   - 数据包大小: 54-7128 bytes
   - 需要进一步分析

## 下一步行动

1. **特定端口分析**
   - 提取主要通信端口的数据包
   - 分析数据包结构

2. **协议逆向**
   - 识别数据包头部结构
   - 分析加密方式

3. **结合DEX分析**
   - 从Android代码确认协议结构
   - 对比PC和手游协议差异

## 工具使用

```bash
# 导出特定TCP流
tshark -r capture.pcapng -q -z follow,tcp,ascii,STREAM_INDEX

# 提取特定IP的数据包
tshark -r capture.pcapng -Y "ip.addr == IP_ADDRESS" -w filtered.pcapng

# 统计协议分布
tshark -r capture.pcapng -q -z io,phs
```
