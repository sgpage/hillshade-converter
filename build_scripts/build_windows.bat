@echo off
REM Build script for Windows
REM Usage: build_scripts\build_windows.bat

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT_DIR=%%~fI"
pushd "%ROOT_DIR%"

echo Building Hillshade Converter for Windows...
echo.

REM Pick Python interpreter (.venv preferred)
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_BIN=.venv\Scripts\python.exe"
    echo Using virtual environment: .venv
) else (
    py -3 --version >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_BIN=py -3"
        echo Using Python launcher: py -3
    ) else (
        python --version >nul 2>&1
        if errorlevel 1 (
            echo Error: Python not found. Please install Python 3.8+
            popd
            exit /b 1
        )
        set "PYTHON_BIN=python"
        echo Using system Python
    )
)

REM Install dependencies
echo Installing dependencies...
%PYTHON_BIN% -m pip install -r requirements.txt

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
%PYTHON_BIN% -m PyInstaller pyinstaller\hillshade_windows.spec

echo.
echo Build complete!
echo Executable created at: dist\hillshade_converter.exe
echo.
echo Next steps:
echo   1. Test the app: dist\hillshade_converter.exe
echo   2. Create release: 7z a Hillshade_Converter_Windows.7z dist\hillshade_converter.exe

popd
