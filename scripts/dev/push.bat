@echo off
echo Pushing Victoria v3.1 Phase8 RC to GitHub...
echo ==============================================

REM Push main branch
echo 1. Pushing main branch...
git push origin main --force-with-lease
if errorlevel 1 (
    echo ERROR: Failed to push main branch
    pause
    exit /b 1
)

REM Remove old tag if exists
echo 2. Removing old tag...
git tag -d "v3.1-20260605-phase8-rc" 2>nul

REM Create new tag
echo 3. Creating tag...
git tag -a "v3.1-20260605-phase8-rc" -m "Victoria v3.1 Phase8 RC: Clean repository with 104 essential files"

REM Push tag
echo 4. Pushing tag...
git push origin "v3.1-20260605-phase8-rc" --force
if errorlevel 1 (
    echo ERROR: Failed to push tag
    pause
    exit /b 1
)

echo.
echo ==============================================
echo Push successful!
echo.
echo Repository: https://github.com/StarsailsClover/MnMCP
echo Tag: v3.1-20260605-phase8-rc
echo.
echo Files: 104
echo Lines: ~4,500
echo Status: Ready for testing
pause
