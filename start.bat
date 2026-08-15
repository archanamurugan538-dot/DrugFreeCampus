@echo off
title DrugFree Campus - Starting...
color 0A

echo.
echo  =====================================================
echo    DrugFree Campus - Anti-Drug Awareness Platform
echo    "Choose Your Future. Stay Safe. Stay Drug-Free."
echo  =====================================================
echo.
echo  Starting application...
echo.

cd /d "%~dp0"

call venv\Scripts\activate.bat

echo  Opening browser...
start "" "http://127.0.0.1:5000"

echo  Server is running at: http://127.0.0.1:5000
echo.
echo  Press Ctrl+C to stop the server.
echo  Do NOT close this window while using the app.
echo  =====================================================
echo.

python app.py

pause
