@echo off
REM Smart Transport System Development Environment Startup Script

echo Starting Smart Transport System development environment...

REM Check if running on Windows
if "%OS%"=="Windows_NT" (
    echo Detected Windows environment
) else (
    echo Error: This script can only run on Windows
    pause
    exit /b 1
)

REM Start backend service
echo Starting backend service...
start "Backend Service" /D "..\backend" python run.py

REM Wait a few seconds for backend service to start
timeout /t 3 /nobreak >nul

REM Start frontend development server
echo Starting frontend development server...
cd ..\frontend
if exist node_modules (
    echo Detected frontend dependencies, starting development server...
    start "Frontend Development Server" npm run dev
) else (
    echo Missing frontend dependencies, installing...
    npm install
    echo Starting frontend development server...
    start "Frontend Development Server" npm run dev
)

echo.
echo ========================================
echo Development environment started successfully!
echo Backend service: http://localhost:5000
echo Frontend development server: http://localhost:3000
echo ========================================
echo

pause