@echo off
setlocal enabledelayedexpansion

:: Check if conda environment exists
conda env list | findstr "ai_scientist" >nul
if errorlevel 1 (
    echo Creating conda environment 'ai_scientist'...
    conda create -n ai_scientist python=3.9 -y
    if errorlevel 1 (
        echo Failed to create conda environment
        exit /b 1
    )
)

:: Activate conda environment
echo Activating conda environment...
call conda activate ai_scientist
if errorlevel 1 (
    echo Failed to activate conda environment
    exit /b 1
)

:: Install requirements if needed
if not exist "requirements.installed" (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install requirements
        exit /b 1
    )
    pip install inquirer
    if errorlevel 1 (
        echo Failed to install inquirer
        exit /b 1
    )
    type nul > requirements.installed
)

:: Run configuration if needed
if not exist "config\ai_scientist_config.json" (
    echo Running configuration wizard...
    python config_ai_scientist.py
    if errorlevel 1 (
        echo Configuration failed
        exit /b 1
    )
) else (
    if "%1"=="--configure" (
        echo Running configuration wizard...
        python config_ai_scientist.py
        if errorlevel 1 (
            echo Configuration failed
            exit /b 1
        )
    )
)

:: Launch the AI Scientist
echo Launching AI Scientist...
python launch_ai_scientist.py %*
if errorlevel 1 (
    echo AI Scientist launch failed
    exit /b 1
)

endlocal