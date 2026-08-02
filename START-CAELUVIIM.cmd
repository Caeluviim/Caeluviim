@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "LOG_DIR=%~dp0logs\launcher"
set "LOG_FILE=%LOG_DIR%\start-latest.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ============================================================
echo Caeluviim graph activation
echo ============================================================
echo Repository: %CD%
echo Log:        %LOG_FILE%
echo.

where docker >nul 2>nul
if errorlevel 1 (
    >"%LOG_FILE%" echo Docker Desktop is not installed or docker.exe is not available on PATH.
    echo ERROR: Docker Desktop is not installed or docker.exe is not available on PATH.
    echo Install or repair Docker Desktop, then run this launcher again.
    echo.
    pause
    exit /b 1
)

docker info >nul 2>nul
if errorlevel 1 (
    >"%LOG_FILE%" echo Docker Desktop is installed but its engine is not running.
    echo ERROR: Docker Desktop is installed but its engine is not running.
    echo Start Docker Desktop, wait until it reports that the engine is running, then run this launcher again.
    echo.
    pause
    exit /b 1
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\laptop\start.ps1" >"%LOG_FILE%" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"

type "%LOG_FILE%"
echo.

if not "%EXIT_CODE%"=="0" (
    echo ============================================================
    echo ACTIVATION FAILED
    echo ============================================================
    echo The full diagnostic record is preserved at:
    echo %LOG_FILE%
    echo.
    pause
    exit /b %EXIT_CODE%
)

echo ============================================================
echo CAELUVIIM GRAPH IS OPERATIONAL
echo ============================================================
echo Neo4j Browser: http://localhost:7474
echo Credentials:   %~dp0.env
echo.
start "Caeluviim Neo4j Browser" "http://localhost:7474"
pause
exit /b 0
