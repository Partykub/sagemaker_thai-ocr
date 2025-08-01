# Installation & Setup

This guide covers the installation of prerequisites, setting up the Python environment, and configuring AWS CLI for SageMaker integration.

## Prerequisites

- Python 3.8+ installed
- Git installed
- Docker (for local testing and SageMaker BYOC)
- AWS CLI configured with appropriate IAM permissions
- Terraform installed

## Python Environment Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   . venv/Scripts/Activate.ps1  # Windows PowerShell
   ```

2. Install project dependencies:
   ```bash
   pip install -r thai-letters/requirements.txt
   pip install paddlepaddle paddleocr
   pip install boto3 sagemaker --upgrade
   ```

3. Verify installation:
   ```bash
   python -c "from paddleocr import PaddleOCR; print(PaddleOCR)"
   ```

## AWS CLI Configuration

1. Configure credentials:
   ```bash
   aws configure
   ```
2. Verify SageMaker access:
   ```bash
   aws sagemaker list-training-jobs
   ```

## Docker Setup (Optional)

- Build the BYOC image:
  ```bash
  docker build -t thai-ocr-paddleocr .
  ```
- Tag and push to ECR:
  ```bash
  aws ecr create-repository --repository-name thai-ocr-paddleocr
  docker tag thai-ocr-paddleocr:latest <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/thai-ocr-paddleocr:latest
  docker push <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/thai-ocr-paddleocr:latest
  ```
