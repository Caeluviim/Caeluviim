@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "LOG_DIR=%~dp0logs\launcher"
set "LOG_FILE=%LOG_DIR%\status-latest.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ============================================================
echo Caeluviim graph status
echo ============================================================
echo Repository: %CD%
echo Log:        %LOG_FILE%
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\laptop\status.ps1" >"%LOG_FILE%" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"

type "%LOG_FILE%"
echo.

if not "%EXIT_CODE%"=="0" (
    echo ============================================================
    echo STATUS CHECK FAILED
    echo ============================================================
    echo The full diagnostic record is preserved at:
    echo %LOG_FILE%
    echo.
    pause
    exit /b %EXIT_CODE%
)

echo Status check completed successfully.
start "Caeluviim Neo4j Browser" "http://localhost:7474"
pause
exit /b 0
