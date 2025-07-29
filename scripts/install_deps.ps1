<#
.SYNOPSIS
    Install Python dependencies for the Thai OCR project in the active virtual environment.
.DESCRIPTION
    Installs required packages from requirements.txt and additional core dependencies.
.EXAMPLE
    . .\scripts\install_deps.ps1
#>

$venvPath = Join-Path $PSScriptRoot 'venv'
# If virtual environment does not exist, create it
if (-Not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found. Running setup_env.ps1 to create it..." -ForegroundColor Yellow
    & "$PSScriptRoot\setup_env.ps1"
}
$activateScript = Join-Path (Join-Path $venvPath 'Scripts') 'Activate.ps1'

if (-Not (Test-Path $activateScript)) {
    Write-Error "Virtual environment not found. Please run setup_env.ps1 first."; exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
. $activateScript

Write-Host "Installing dependencies from thai-letters/requirements.txt..." -ForegroundColor Cyan
$reqFile = Join-Path $PSScriptRoot '..\thai-letters\requirements.txt'
if (-Not (Test-Path $reqFile)) { Write-Error "requirements.txt not found at $reqFile"; exit 1 }
pip install -r $reqFile
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install requirements.txt"; exit $LASTEXITCODE }

Write-Host "Installing core dependencies: paddlepaddle, paddleocr, boto3, sagemaker..." -ForegroundColor Cyan
pip install paddlepaddle paddleocr boto3 sagemaker
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install core dependencies"; exit $LASTEXITCODE }

Write-Host "All dependencies installed successfully." -ForegroundColor Green
