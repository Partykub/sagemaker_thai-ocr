@echo off
chcp 65001 >nul
echo 🔥 Quick Phase 1: Thai Dataset to PaddleOCR Converter
echo ====================================================
echo.

cd /d "%~dp0"

echo 🐍 Running Python converter...
python quick_phase1_converter.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Conversion completed successfully!
    echo 📁 Your PaddleOCR dataset is ready for training
    echo.
    echo 🚀 Next steps:
    echo 1. Install PaddleOCR: pip install paddlepaddle-gpu paddleocr
    echo 2. Start training with the generated config file
    echo.
) else (
    echo.
    echo ❌ Conversion failed. Please check the error messages above.
    echo.
)

pause
