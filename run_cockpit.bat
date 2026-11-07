@echo off
setlocal
echo ===================================================
echo Starting PayGuard Swarm - Interactive Cockpit UI
echo ===================================================

set "PY_EXE="

if exist "%LOCALAPPDATA%\Programs\Python311\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python311\python.exe"
) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) else if exist "C:\Program Files\Python311\python.exe" (
    set "PY_EXE=C:\Program Files\Python311\python.exe"
) else (
    set "PY_EXE=python"
)

echo Using Python: "%PY_EXE%"
echo Opening Cockpit in your default browser...
start "" http://localhost:8501
"%PY_EXE%" -m streamlit run frontend\app.py --server.port 8501
pause
