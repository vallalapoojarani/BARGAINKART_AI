@echo off
title BARGAINKART - AI E-Commerce Platform
color 0B
cls

echo ===============================================================================
echo                BARGAINKART - AI-POWERED E-COMMERCE PLATFORM
echo         "Compare. Verify. Bargain. Save." (Dual SQLite + MongoDB)
echo ===============================================================================
echo.

cd /d "%~dp0"

echo [*] Checking Python environment...
if exist "%USERPROFILE%\anaconda3\python.exe" (
    set "PY_CMD=%USERPROFILE%\anaconda3\python.exe"
) else (
    python --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        py --version >nul 2>&1
        if %ERRORLEVEL% NEQ 0 (
            echo [!] Python was not found in your standard PATH.
            echo [*] Attempting to locate Python via WindowsApps...
            if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
                set "PY_CMD=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
            ) else (
                echo [X] Could not find Python. Please install Python 3.10+ from python.org
                pause
                exit /b 1
            )
        ) else (
            set "PY_CMD=py"
        )
    ) else (
        set "PY_CMD=python"
    )
)

echo [*] Using Python: %PY_CMD%
echo.
echo ===============================================================================
echo  PLATFORM SERVICES & URLS:
echo  - Home Dashboard:           http://127.0.0.1:5000/
echo  - Game Zone (5 Games):      http://127.0.0.1:5000/game-zone (Rs. 300 -> Rs. 270)
echo  - Festival Offers (8 Tabs): http://127.0.0.1:5000/festival-offers (Rs. 200 -> Rs. 180)
echo  - AI Negotiator Studio:     http://127.0.0.1:5000/negotiate-center (Voice + Robot)
echo  - Price Transparency Hub:   http://127.0.0.1:5000/compare (500 Products Safe/Risk)
echo  - Admin Control Centre:     http://127.0.0.1:5000/admin/dashboard
echo  - About Team & Guide:       http://127.0.0.1:5000/about
echo.
echo  SEPARATE SYSTEM ADMIN & ACADEMIC CREDENTIALS (UCETW - KAKATIYA UNIVERSITY):
echo  - System Administrator:     admin                 ^| Password: admin
echo  - Project Guide:            smt.p.vaishnavi       ^| Password: vaishnavi
echo  - V. Poojarani:             23568T3055            ^| Password: poojarani
echo  - P. Anusha:                245683064L            ^| Password: anusha
echo  - G. Deepika:               23568T3018            ^| Password: deepika
echo  - D. Pavani Alekhya:        23568T3012            ^| Password: pavani
echo  - K. Prathyusha:            23568T3029            ^| Password: prathyusha
echo  - Demo Customer:            demo@bargainkart.com  ^| Password: Demo@123
echo ===============================================================================
echo.
echo [*] Launching BARGAINKART Application Server...
echo [*] Press CTRL+C at any time to stop the server.
echo.

start "" http://127.0.0.1:5000 2>nul
%PY_CMD% run.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Server exited with an error code: %ERRORLEVEL%
    pause
)
