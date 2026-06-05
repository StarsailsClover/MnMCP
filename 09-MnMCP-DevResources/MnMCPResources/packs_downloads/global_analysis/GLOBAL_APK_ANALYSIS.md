# 迷你世界外服APK分析报告

## 分析时间
2026-02-26 14:07:51

## APK基本信息

### 国服APK
- **文件名**: miniworldMini-wp.apk
- **大小**: 1641.40 MB
- **文件数**: 4036
- **库文件数**: 157
- **架构**: arm64-v8a, armeabi-v7a

### 外服APK
- **文件名**: miniworld_en_1.7.15.apk
- **大小**: 1011.06 MB
- **文件数**: 3414
- **库文件数**: 28
- **架构**: armeabi-v7a

## 差异对比

| 项目 | 国服 | 外服 | 差异 |
|------|------|------|------|
| 大小 | 1641.40 MB | 1011.06 MB | -630.34 MB |
| 文件数 | 4036 | 3414 | -622 |
| 库文件 | 157 | 28 | -129 |

## 外服特有功能

### 登录方式
- google
- twitter
- apple
- facebook

### 支付系统
- 未识别

### 社交平台集成
- youtube

### 服务器区域
- us
- eu
- asia
- global
- server
- region

## 协议差异预期

基于APK分析，预期外服与国服在以下方面存在差异：

1. **登录认证**
   - 国服：迷你号/手机号 + 国内登录SDK
   - 外服：Google/Facebook OAuth + Firebase

2. **加密算法**
   - 国服：AES-128-CBC（预期）
   - 外服：AES-256-GCM（预期）

3. **服务器地址**
   - 国服：mini1.cn 域名
   - 外服：playmini.net 或其他国际域名

4. **内容审查**
   - 国服：有内容审查和防沉迷
   - 外服：相对宽松

## 下一步分析建议

1. **反编译外服APK**（如果尚未完成）
   - 使用jadx查看完整源码
   - 定位网络通信类

2. **对比协议实现**
   - 查找外服服务器地址
   - 分析登录流程差异
   - 识别加密算法

3. **抓包分析**
   - 安装外服APK到设备
   - 使用Wireshark抓包
   - 对比国服/外服数据包结构

## 文件位置

- 外服APK: `MnMCPResources/packs_downloads/miniworld_en_1.7.15.apk`
- 反编译源码: `MnMCPResources/packs_downloads/global_analysis/sources/`
