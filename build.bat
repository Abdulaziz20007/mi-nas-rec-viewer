@echo off
REM Build script for NAS Camera Viewer Windows executable

echo Building NAS Camera Viewer...
echo.

REM Check if python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyQt6 is not installed
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller is not installed
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Create build directory
if not exist build mkdir build

REM Run PyInstaller
echo Building executable...
if exist build.spec (
    pyinstaller build.spec --noconfirm --clean
) else if exist NASCameraViewer.spec (
    pyinstaller NASCameraViewer.spec --noconfirm --clean
) else (
    pyinstaller --noconfirm --clean --onefile --windowed --name NASCameraViewer app.py
)

REM Check if build was successful
if exist "dist\NASCameraViewer.exe" (
    echo.
    echo ==========================================
    echo Build completed successfully!
    echo.
    echo Executable location: dist\NASCameraViewer.exe
    echo File size: 
    for %%I in ("dist\NASCameraViewer.exe") do echo   %%~zI bytes
    echo.
    echo You can now distribute the executable file.
    echo ==========================================
    echo.
) else (
    echo.
    echo ==========================================
    echo Build FAILED!
    echo.
    echo Check the output above for error messages.
    echo Common issues:
    echo - Missing Python dependencies
    echo - Antivirus blocking PyInstaller
    echo ==========================================
    echo.
)

pause
