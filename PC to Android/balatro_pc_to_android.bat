@echo off
REM Change to the directory of this batch file
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed or not in PATH
    pause
    exit /b
)

echo Installing required Python packages...
pip install requests

echo Running backup tool...
python pc_to_android.py
pause
