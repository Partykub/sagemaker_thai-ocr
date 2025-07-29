<#
.SYNOPSIS
    Configure AWS CLI credentials and verify permissions for the Thai OCR project.
.DESCRIPTION
    Prompts for AWS Access Key, Secret Key, default region, and output format,
    then tests common AWS CLI commands to verify access.
.PARAMETER Profile
    The AWS CLI profile name. Default is 'default'.
.PARAMETER Region
    The AWS region to set. Default is 'ap-southeast-1'.
.PARAMETER OutputFormat
    The AWS CLI output format. Default is 'json'.
.PARAMETER AccessKey
    The AWS Access Key ID.
.PARAMETER SecretKey
    The AWS Secret Access Key.
.PARAMETER SessionToken
    The AWS Session Token (optional).
.EXAMPLE
    .\configure_aws_cli.ps1 -Profile "thai-ocr" -Region "ap-southeast-1" -OutputFormat "json" -AccessKey "your_access_key" -SecretKey "your_secret_key"
#>
param(
    [string]$Profile = 'default',
    [string]$Region = 'ap-southeast-1',
    [string]$OutputFormat = 'json',
    [string]$AccessKey = '',   # AWS Access Key ID
    [string]$SecretKey = '',   # AWS Secret Access Key
    [string]$SessionToken = '' # AWS Session Token (optional)
)

Write-Host "Configuring AWS CLI for profile '$Profile'..." -ForegroundColor Cyan
aws configure set region $Region --profile $Profile
aws configure set output $OutputFormat --profile $Profile

# Configure credentials if provided, else prompt interactively
if ($AccessKey -and $SecretKey) {
    aws configure set aws_access_key_id $AccessKey --profile $Profile
    aws configure set aws_secret_access_key $SecretKey --profile $Profile
    if ($SessionToken) {
        aws configure set aws_session_token $SessionToken --profile $Profile
    }
} else {
    aws configure --profile $Profile
}

Write-Host "`nVerifying AWS CLI configuration and permissions..." -ForegroundColor Cyan

# Run verification steps and exit on any error
$verifyCommands = @(
    { aws sts get-caller-identity --profile $Profile },
    { aws s3 ls --profile $Profile },
    { aws sagemaker list-training-jobs --profile $Profile }
)

foreach ($cmd in $verifyCommands) {
    & $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Verification command failed." -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Write-Host "`nAWS CLI configuration complete." -ForegroundColor Green
