@echo off
echo ========================================
echo Install mitmproxy Certificate
echo ========================================
echo.

set CERT_FILE=%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.p12

if not exist "%CERT_FILE%" (
    echo [ERROR] Certificate not found!
    echo Please start mitmproxy first to generate certificate.
    pause
    exit /b 1
)

echo [OK] Certificate found: %CERT_FILE%
echo.
echo Installing certificate to Trusted Root...
echo.

certutil -f -user -p "" -importpfx Root "%CERT_FILE%"

if %errorlevel% == 0 (
    echo.
    echo [OK] Certificate installed successfully!
    echo.
    echo You can now use mitmproxy to intercept HTTPS traffic.
) else (
    echo.
    echo [ERROR] Installation failed!
    echo.
    echo Please try manual installation:
    echo 1. Open: %CERT_FILE%
    echo 2. Store Location: Current User
    echo 3. Certificate Store: Trusted Root Certification Authorities
)

echo.
pause
