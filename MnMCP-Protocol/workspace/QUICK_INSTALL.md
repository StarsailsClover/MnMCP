# Quick Install Guide

## Current Status

You have Python 3.11.9 (built-in, no pip)
Need: Full Python with pip

## Install Steps

### 1. Download Python

Visit: https://www.python.org/downloads/

Download: **Python 3.11.9** (Windows installer 64-bit)

Direct link: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

### 2. Install Python

1. Run the downloaded installer
2. ✅ **CHECK "Add Python to PATH"** (IMPORTANT!)
3. Click "Install Now"
4. Wait for completion

### 3. Verify Installation

Open **NEW** Command Prompt and run:
```cmd
py -m pip --version
```

Should show: `pip 23.x.x`

### 4. Install mitmproxy

```cmd
py -m pip install mitmproxy
```

### 5. Verify mitmproxy

```cmd
py -m mitmproxy.tools.mitmdump --version
```

### 6. Start mitmproxy

```cmd
cd D:\Coding\BlockConnect\BlockConnect-MnMCP\workspace
py -m mitmproxy.tools.mitmdump -s mnmcp_websocket_interceptor.py --listen-host 127.0.0.1 --listen-port 8080
```

---

## Quick Commands

```cmd
# Download Python
start https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

# After installation, install mitmproxy
py -m pip install mitmproxy

# Start mitmproxy
cd D:\Coding\BlockConnect\BlockConnect-MnMCP\workspace
py -m mitmproxy.tools.mitmdump -s mnmcp_websocket_interceptor.py --listen-host 127.0.0.1 --listen-port 8080
```

---

## Alternative: Use Portable Python

If you don't want to install Python system-wide, download portable version:

https://github.com/winpython/winpython/releases

---

**Estimated time: 10 minutes**
