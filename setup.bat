@echo off
setlocal

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_COMMAND=py -3"
) else (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Python 3 is required but was not found.
        exit /b 1
    )
    set "PYTHON_COMMAND=python"
)

if not exist ".venv" (
    echo Creating virtual environment...
    call %PYTHON_COMMAND% -m venv .venv
    if errorlevel 1 exit /b 1
)

echo Activating virtual environment...
call ".venv\Scripts\activate.bat"
if errorlevel 1 exit /b 1

echo Installing Flask...
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

python -m pip install Flask
if errorlevel 1 exit /b 1

echo Initializing database...
python -c "from app import create_app; create_app(); print('Database initialized.')"
if errorlevel 1 exit /b 1

echo Starting server at http://127.0.0.1:5000
python app.py
