@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "BUNDLED_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%BUNDLED_PY%" (
    "%BUNDLED_PY%" windows\start.py
) else (
    where py >nul 2>&1
    if errorlevel 1 (
        python windows\start.py
    ) else (
        py -3 windows\start.py
    )
)
if errorlevel 1 pause
