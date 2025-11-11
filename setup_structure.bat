@echo off
setlocal enabledelayedexpansion

echo Setting up project structure...
echo ==============================

:: Define the base directory structure
set "BASE_DIR=src\ai_engg"
set "STATIC_DIR=%BASE_DIR%\static"
set "TEMPLATES_DIR=%BASE_DIR%\templates"

:: Create main directories
for %%d in (
    "%BASE_DIR%"
    "%BASE_DIR%\core"
    "%BASE_DIR%\api"
    "%BASE_DIR%\utils"
    "%BASE_DIR%\config"
    "%STATIC_DIR%"
    "%STATIC_DIR%\css"
    "%STATIC_DIR%\js"
    "%STATIC_DIR%\images"
    "%TEMPLATES_DIR%"
    "tests"
    "docs"
    "logs"
    "uploads"
) do (
    if not exist "%%~d" (
        mkdir "%%~d"
        if !errorlevel! neq 0 (
            echo Failed to create directory: %%~d
            exit /b 1
        )
    )
)

:: Create __init__.py files
for %%f in (
    "%BASE_DIR%\__init__.py"
    "%BASE_DIR%\core\__init__.py"
    "%BASE_DIR%\api\__init__.py"
    "%BASE_DIR%\utils\__init__.py"
    "%BASE_DIR%\config\__init__.py"
) do (
    if not exist "%%~f" (
        echo. > "%%~f"
    )
)

:: Create main.py if it doesn't exist
if not exist "src\main.py" (
    (
        echo from ai_engg.app import app, assistant
        echo.
        echo if __name__ == '__main__':
        echo     app.run(host='0.0.0.0', port=5001, debug=True)
    ) > "src\main.py"
)

:: Copy static files if they exist
if exist "static\*" (
    xcopy /E /I /Y "static\*" "%STATIC_DIR%\" >nul
)

:: Copy template files if they exist
if exist "templates\*" (
    xcopy /E /I /Y "templates\*" "%TEMPLATES_DIR%\" >nul
)

echo Project structure has been set up successfully!
echo.
echo Next steps:
echo 1. Move your application files to the appropriate directories:
echo    - Main application: src\ai_engg\app.py
echo    - Core modules: src\ai_engg\core\
echo    - API endpoints: src\ai_engg\api\
echo    - Configuration: src\ai_engg\config\
echo.
echo 2. Run the application using:
echo    python -m src.main
echo.

pause
