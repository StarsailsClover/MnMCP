@echo off
echo ========================================
echo MnMCP - Setup and Start Complete Server
echo ========================================
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Please run as Administrator!
    echo.
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b 1
)

echo [OK] Running as Administrator
echo.

echo ========================================
echo Step 1: Backup and modify hosts file
echo ========================================
echo.

:: Create backup with timestamp
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
copy C:\Windows\System32\drivers\etc\hosts C:\Windows\System32\drivers\etc\hosts.backup.%TIMESTAMP%

echo [OK] Backup created: hosts.backup.%TIMESTAMP%
echo.

:: Add MnMCP entries
echo. >> C:\Windows\System32\drivers\etc\hosts
echo # MnMCP - MiniWorld Server Redirection >> C:\Windows\System32\drivers\etc\hosts
echo 127.0.0.1 openroom.mini1.cn >> C:\Windows\System32\drivers\etc\hosts
echo 127.0.0.1 shequ.mini1.cn >> C:\Windows\System32\drivers\etc\hosts
echo 127.0.0.1 125.88.252.175 >> C:\Windows\System32\drivers\etc\hosts
echo 127.0.0.1 42.240.175.30 >> C:\Windows\System32\drivers\etc\hosts
echo 127.0.0.1 1.13.213.183 >> C:\Windows\System32\drivers\etc\hosts
echo 127.0.0.1 1.13.213.198 >> C:\Windows\System32\drivers\etc\hosts
echo 127.0.0.1 1.13.213.236 >> C:\Windows\System32\drivers\etc\hosts

echo [OK] Hosts file modified
echo.

echo ========================================
echo Step 2: Flush DNS cache
echo ========================================
echo.
ipconfig /flushdns
echo.

echo ========================================
echo Step 3: Start servers
echo ========================================
echo.

cd /d "%~dp0"

echo Starting HTTP Server (Port 8080)...
start "MnMCP HTTP Server" cmd /k "C:\Users\Sails\AppData\Local\Programs\Python\Python314\python.exe miniworld_http_server.py"

timeout /t 2 /nobreak >nul

echo Starting WebSocket RPC Server (Port 8081)...
start "MnMCP WebSocket RPC" cmd /k "C:\Users\Sails\AppData\Local\Programs\Python\Python314\python.exe miniworld_rpc_server.py"

echo.
echo ========================================
echo [OK] All servers started!
echo ========================================
echo.
echo Servers:
echo   - HTTP API: http://127.0.0.1:8080
echo   - WebSocket RPC: ws://127.0.0.1:8081
echo.
echo Next steps:
echo 1. Close Proxifier (not needed anymore)
echo 2. Open MiniWorld
echo 3. Login with any account (fake auth)
echo 4. Check room list - you should see Minecraft room!
echo.
echo Press any key to close this window...
pause >nul
