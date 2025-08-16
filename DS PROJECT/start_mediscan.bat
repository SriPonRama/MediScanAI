@echo off
echo ========================================
echo    MediScan AI - Starting Application
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Starting MediScan AI...
echo.
echo ========================================
echo   Application will be available at:
echo   http://localhost:5000
echo.
echo   Demo Login:
echo   Email: demo@mediscan.com
echo   Password: demo123
echo ========================================
echo.
echo Press Ctrl+C to stop the application
echo.

python app.py

echo.
echo MediScan AI has stopped.
pause
