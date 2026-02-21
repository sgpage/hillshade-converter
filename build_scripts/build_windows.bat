@echo off
REM Build script for Windows
REM Usage: build_scripts\build_windows.bat

setlocal enabledelayedexpansion

echo Building Hillshade Converter for Windows...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Clean previous builds
if exist build (
    echo Cleaning previous build...
    rmdir /s /q build
)
if exist dist (
    rmdir /s /q dist
)

REM Build with PyInstaller
echo Building with PyInstaller...
pyinstaller pyinstaller\hillshade_windows.spec

echo.
echo Build complete!
echo Executable created at: dist\hillshade_converter.exe
echo.
echo Next steps:
echo   1. Test the app: dist\hillshade_converter.exe
echo   2. Create release: 7z a Hillshade_Converter_Windows.7z dist\hillshade_converter.exe
