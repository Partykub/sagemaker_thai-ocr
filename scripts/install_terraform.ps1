<#
.SYNOPSIS
    Install Terraform CLI and initialize the Terraform project.
.DESCRIPTION
    Checks for Terraform installation, installs via Chocolatey if missing,
    and initializes Terraform in the project root.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\scripts\install_terraform.ps1
#>

Write-Host "Checking Terraform installation..." -ForegroundColor Cyan
if (-Not (Get-Command terraform -ErrorAction SilentlyContinue)) {
    Write-Host "Terraform CLI not found. Please install Terraform (e.g., put terraform.exe in a PATH folder) and restart PowerShell: https://www.terraform.io/downloads.html" -ForegroundColor Red
    exit 1
}
Write-Host "Terraform CLI is installed." -ForegroundColor Green


Write-Host "Initializing Terraform project..." -ForegroundColor Cyan
terraform init
if ($LASTEXITCODE -ne 0) {
    Write-Host "Terraform init failed." -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "Terraform initialization complete." -ForegroundColor Green
