@echo off
echo ========================================
echo   Creating MediScan AI Desktop Shortcut
echo ========================================
echo.

set "SCRIPT_DIR=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT_NAME=MediScan AI.lnk"

echo Creating shortcut on Desktop...

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\%SHORTCUT_NAME%'); $Shortcut.TargetPath = '%SCRIPT_DIR%start_mediscan.bat'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = 'MediScan AI - AI-Powered Medical Diagnosis'; $Shortcut.Save()}"

if exist "%DESKTOP%\%SHORTCUT_NAME%" (
    echo.
    echo ✅ SUCCESS! Desktop shortcut created successfully!
    echo.
    echo 📋 How to use:
    echo 1. Double-click "MediScan AI" shortcut on your Desktop
    echo 2. Wait for the application to start
    echo 3. Open browser and go to: http://localhost:5000
    echo 4. Login with: demo@mediscan.com / demo123
    echo.
    echo 🎉 MediScan AI is now ready to use anytime!
) else (
    echo.
    echo ❌ ERROR: Could not create desktop shortcut
    echo Please manually create a shortcut to start_mediscan.bat
)

echo.
pause
