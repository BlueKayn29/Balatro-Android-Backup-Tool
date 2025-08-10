@echo off
where python >nul 2>nul
if errorlevel 1 (
	echo Python is not installed or not in PATH
	pause
	exit /b
)

echo Installing required Python packages...
pip install requests

echo Running backup tool...
python backup_tool.py
pause