@echo off
echo ========================================
echo MnMCP - Enable System Proxy
echo ========================================
echo.

echo Setting system proxy: 127.0.0.1:7890
netsh winhttp set proxy 127.0.0.1:7890

echo.
echo [OK] Proxy enabled!
echo.
echo Now you can open MiniWorld and check room list
echo.
echo After testing, run disable_proxy.bat to disable proxy
echo.
pause
