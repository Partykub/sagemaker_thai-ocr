<#
.SYNOPSIS
    Create and provide instructions to activate a Python virtual environment.
.DESCRIPTION
    This script creates a Python virtual environment folder and prints the command to activate it in PowerShell.
.PARAMETER EnvName
    The name of the virtual environment folder. Default is 'venv'.
.EXAMPLE
    . .\setup_env.ps1
    .\setup_env.ps1 -EnvName "env"
#>
param(
    [string]$EnvName = "venv"
)

$EnvPath = Join-Path $PSScriptRoot $EnvName

if (-Not (Test-Path $EnvPath)) {
    Write-Host "Creating Python virtual environment at '$EnvPath'..." -ForegroundColor Cyan
    python -m venv $EnvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment."; exit $LASTEXITCODE
    }
} else {
    Write-Host "Virtual environment already exists at '$EnvPath'." -ForegroundColor Yellow
}

Write-Host "To activate the virtual environment, run:" -ForegroundColor Green
Write-Host ". '$EnvPath/Scripts/Activate.ps1'" -ForegroundColor White
