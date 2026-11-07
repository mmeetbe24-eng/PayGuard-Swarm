@echo off
setlocal
echo ===================================================
echo Starting PayGuard Swarm - FastAPI REST Backend
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
"%PY_EXE%" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause
