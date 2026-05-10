@echo off
REM Batch script to activate venv and run the app
echo ======================================================================
echo SHEEP FIN-MITRA - Starting Application
echo ======================================================================

REM Check for .venv in current directory
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment: .venv
    call .venv\Scripts\activate.bat
    goto :run_app
)

REM Check for .venv in parent directory
if exist "..\..venv\Scripts\activate.bat" (
    echo Activating virtual environment: ..\..venv
    call ..\..venv\Scripts\activate.bat
    goto :run_app
)

REM Check for venv in current directory
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment: venv
    call venv\Scripts\activate.bat
    goto :run_app
)

echo No virtual environment found. Using system Python.
echo.

:run_app
echo.
echo Checking Python environment...
python --version
python -c "import sys; print('Python path:', sys.executable)"
echo.

echo Checking bcrypt...
python -c "import bcrypt; print('bcrypt version:', bcrypt.__version__)" 2>nul
if errorlevel 1 (
    echo bcrypt is not installed. Installing...
    python -m pip install bcrypt
)

echo.
echo Starting application...
echo ======================================================================
python app_fin_mitra.py

pause

