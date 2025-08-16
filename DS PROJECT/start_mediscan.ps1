# MediScan AI - PowerShell Startup Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   MediScan AI - Starting Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting MediScan AI..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Application will be available at:" -ForegroundColor Green
Write-Host "  http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "  Demo Login:" -ForegroundColor Green
Write-Host "  Email: demo@mediscan.com" -ForegroundColor White
Write-Host "  Password: demo123" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

# Start the application
try {
    python app.py
} catch {
    Write-Host ""
    Write-Host "Error starting application: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "MediScan AI has stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
