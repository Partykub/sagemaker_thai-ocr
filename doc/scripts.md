# Script Reference

> **Note:** Update this document (`doc/scripts.md`) whenever adding or modifying scripts in the `scripts/` directory.

This document describes the purpose and usage of each custom script in the `scripts/` directory.

## setup_env.ps1

- **Location:** `scripts/setup_env.ps1`
- **Purpose:** Create a Python virtual environment (`venv`) in the project’s `scripts/` folder.
- **Usage:**
  ```powershell
  # Run without parameters to create default 'venv'
  powershell -ExecutionPolicy Bypass -File .\scripts\setup_env.ps1
  ```
- **Behavior:**
  - If the `venv` folder does not exist, it creates one using `python -m venv venv`.
  - Prints the command to activate the environment in PowerShell.

## install_deps.ps1

- **Location:** `scripts/install_deps.ps1`
- **Purpose:** Install all required Python packages in the active virtual environment.
- **Usage:**
  ```powershell
  # This script will auto-create venv if missing, activate it, and install dependencies
  powershell -ExecutionPolicy Bypass -File .\scripts\install_deps.ps1
  ```
- **Behavior:**
  1. Ensures a `venv` exists by invoking `setup_env.ps1` if needed.
  2. Activates the virtual environment.
  3. Installs packages listed in `thai-letters/requirements.txt`.
  4. Installs core dependencies: `paddlepaddle`, `paddleocr`, `boto3`, `sagemaker`.
  5. Exits with an error if any step fails.

---

## configure_aws_cli.ps1

- **Location:** `scripts/configure_aws_cli.ps1`
- **Purpose:** Configure AWS CLI credentials and verify permissions for the Thai OCR project.
- **Status:** ✅ **Completed and tested**
- **Usage:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\configure_aws_cli.ps1 -Profile <profile> [-Region <region>] [-OutputFormat <format>] [-AccessKey <key>] [-SecretKey <secret>] [-SessionToken <token>]
  ```
- **Behavior:**
  1. Sets AWS CLI region and output format via `aws configure set`.
  2. Applies AWS credentials non-interactively if provided; otherwise, prompts via `aws configure`.
  3. Verifies setup using `aws sts get-caller-identity`, `aws s3 ls`, and `aws sagemaker list-training-jobs`.
  4. Includes fallback AWS CLI installation if command not found.
  5. Exits with an error if any verification command fails.

---

## install_terraform.ps1

- **Location:** `scripts/install_terraform.ps1`
- **Purpose:** Check Terraform installation and initialize the Terraform project.
- **Status:** ✅ **Completed and tested**
- **Usage:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\scripts\install_terraform.ps1
  ```
- **Behavior:**
  1. Checks for `terraform` command availability.
  2. If Terraform not found, provides manual installation instructions.
  3. Runs `terraform init` to download providers and set up the working directory.
  4. Simplified to focus on verification and initialization rather than automated installation.
  5. Exits with appropriate status codes.

Keep this file updated when adding or modifying scripts in `scripts/`.
