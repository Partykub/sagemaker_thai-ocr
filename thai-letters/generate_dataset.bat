@echo off
REM 🔥 Windows Batch Script for Phase 1 Thai Dataset Generation
REM ใช้สำหรับ Windows PowerShell/Command Prompt

echo ===============================================
echo 🔥 Thai OCR Dataset Generation - Phase 1
echo ===============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found in PATH
    echo Please install Python and add it to PATH
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Show menu
echo 📋 Choose dataset size:
echo    1. Small (5 samples per character) - Quick test
echo    2. Standard (10 samples per character) - Recommended
echo    3. Large (20 samples per character) - High quality
echo    4. Custom (enter your own number)
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" (
    set samples=5
    echo 🎯 Selected: Small dataset (5 samples)
) else if "%choice%"=="2" (
    set samples=10
    echo 🎯 Selected: Standard dataset (10 samples)
) else if "%choice%"=="3" (
    set samples=20
    echo 🎯 Selected: Large dataset (20 samples)
) else if "%choice%"=="4" (
    set /p samples=Enter number of samples per character (1-100): 
    echo 🎯 Selected: Custom dataset (%samples% samples)
) else (
    echo ❌ Invalid choice. Using default (10 samples)
    set samples=10
)

echo.
echo 🚀 Starting dataset generation...
echo 📊 Samples per character: %samples%
echo.

REM Change to script directory
cd /d "%~dp0"

REM Run the generator
python quick_phase1_generator.py %samples%

if errorlevel 1 (
    echo.
    echo ❌ Dataset generation failed!
    echo Please check the error messages above
) else (
    echo.
    echo ✅ Dataset generation completed successfully!
    echo 📁 Check the generated folder for your dataset
)

echo.
echo Press any key to exit...
pause >nul
