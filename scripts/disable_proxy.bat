@echo off
echo ========================================
echo MnMCP - Disable System Proxy
echo ========================================
echo.

echo Disabling system proxy...
netsh winhttp reset proxy

echo.
echo [OK] Proxy disabled!
echo.
pause
