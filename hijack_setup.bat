@echo off
chcp 65001 >nul 2>&1

if "%1"=="on" goto ENABLE
if "%1"=="off" goto DISABLE

echo Usage:
echo   hijack_setup.bat on   - enable hijack
echo   hijack_setup.bat off  - disable hijack
goto END

:ENABLE
echo [1/2] Adding route: 60.204.1.188 to loopback
route add 60.204.1.188 mask 255.255.255.255 127.0.0.1 IF 1
echo [2/2] Adding portproxy: 60.204.1.188:80 to 127.0.0.1:80
netsh interface portproxy add v4tov4 listenaddress=60.204.1.188 listenport=80 connectaddress=127.0.0.1 connectport=80
echo.
echo HIJACK ON. Now run: python mn2mc_test_connect.py
echo Then start MiniWorld and join a room.
echo After test run: hijack_setup.bat off
goto END

:DISABLE
echo [1/2] Deleting route
route delete 60.204.1.188 >nul 2>&1
echo [2/2] Deleting portproxy
netsh interface portproxy delete v4tov4 listenaddress=60.204.1.188 listenport=80 >nul 2>&1
echo.
echo HIJACK OFF. Network restored.
goto END

:END
echo.
netsh interface portproxy show all
pause
