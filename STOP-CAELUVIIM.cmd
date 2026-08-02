@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "LOG_DIR=%~dp0logs\launcher"
set "LOG_FILE=%LOG_DIR%\stop-latest.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ============================================================
echo Caeluviim graph shutdown
echo ============================================================
echo Repository: %CD%
echo Log:        %LOG_FILE%
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\laptop\stop.ps1" >"%LOG_FILE%" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"

type "%LOG_FILE%"
echo.

if not "%EXIT_CODE%"=="0" (
    echo ============================================================
    echo SHUTDOWN FAILED
    echo ============================================================
    echo The full diagnostic record is preserved at:
    echo %LOG_FILE%
    echo.
    pause
    exit /b %EXIT_CODE%
)

echo Caeluviim graph services stopped. Persistent graph volumes were preserved.
pause
exit /b 0
