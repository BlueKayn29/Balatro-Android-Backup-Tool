@echo off
for /f "delims=" %%i in ('where python 2^>nul') do (
    echo %%i | find /i "WindowsApps" >nul
    if errorlevel 1 (
        set "PYTHON_PATH=%%i"
        goto found
    )
)

echo Python is not installed or not in PATH
pause
exit /b

:found
echo Found Python at %PYTHON_PATH%
echo Installing required Python packages...
pip install requests

echo.
echo Running transfer tool...
python pc_to_android.py
pause
