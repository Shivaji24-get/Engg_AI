@echo off
echo Creating backup directory...
mkdir backup_%date:/=%-%time::=-% 2>nul

echo Backing up important files...
xcopy app.py backup_%date:/=%-%time::=-%\ /Y
xcopy assistant_openrouter.py backup_%date:/=%-%time::=-%\ /Y
xcopy requirements.txt backup_%date:/=%-%time::=-%\ /Y
xcopy readme.md backup_%date:/=%-%time::=-%\ /Y
xcopy config.py backup_%date:/=%-%time::=-%\ /Y 2>nul
xcopy templates backup_%date:/=%-%time::=-%\templates /E /I /Y
xcopy static backup_%date:/=%-%time::=-%\static /E /I /Y

echo Cleaning up...
rmdir /s /q venv
rmdir /s /q __pycache__
del /q *.log
rd /s /q tools
rd /s /q prompts
del /q ce3.py
del /q test.py
del /q ui.png
del /q uv.lock
del /q pyproject.toml

echo Creating new virtual environment...
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo Cleanup complete! Your files have been backed up to: backup_%date:/=%-%time::=-%\
pause
