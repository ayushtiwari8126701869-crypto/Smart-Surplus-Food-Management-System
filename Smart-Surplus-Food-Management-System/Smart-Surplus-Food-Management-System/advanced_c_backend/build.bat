@echo off
echo Compiling backend.c ...
gcc -shared -o backend.dll backend.c
if errorlevel 1 (
    echo.
    echo Compile failed. Check that gcc is installed: gcc --version
    pause
    exit /b 1
)
echo Done! Starting the app...
python gui.py
pause
