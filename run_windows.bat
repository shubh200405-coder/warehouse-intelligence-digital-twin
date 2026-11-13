@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if not errorlevel 1 (
    set "PYTHON=py"
) else (
    where python >nul 2>&1
    if not errorlevel 1 set "PYTHON=python"
)

if not defined PYTHON (
    echo Python was not found. Install Python 3.10 or later and enable Add to PATH.
    goto :error
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :error
)

echo Installing project dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo Opening Warehouse Intelligence at http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto :error
goto :eof

:error
echo.
echo Setup or launch failed. Review the error above.
pause
exit /b 1
