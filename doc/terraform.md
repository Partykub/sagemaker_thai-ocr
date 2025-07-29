# Infrastructure as Code (Terraform)

This document details the Terraform configuration for provisioning AWS resources required for Thai OCR training and deployment.

## Providers and Variables

```hcl
provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "ap-southeast-1"
}

variable "project_id" {
  type = string
}

variable "environment" {
  type    = string
  default = "dev"
}
```

## Resources

### S3 Bucket

```hcl
resource "aws_s3_bucket" "thai_ocr_bucket" {
  bucket = "thai-ocr-${var.project_id}-${var.environment}"
  acl    = "private"

  versioning {
    enabled = true
  }
}
```

### ECR Repository

```hcl
resource "aws_ecr_repository" "thai_ocr_repo" {
  name = "thai-ocr-paddleocr"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration { scan_on_push = true }
}
```

### IAM Roles

```hcl
resource "aws_iam_role" "sagemaker_role" {
  name = "sagemaker-thai-ocr-role-${var.environment}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      { Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "sagemaker.amazonaws.com" }}
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sagemaker_s3" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "sagemaker_ecr" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonECRFullAccess"
}
```

### Lambda Function

```hcl
resource "aws_lambda_function" "start_training" {
  function_name = "start-thai-ocr-training-${var.environment}"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.10"
  role          = aws_iam_role.lambda_role.arn
  filename      = "lambda_start_training.zip"
  timeout       = 60
  environment {
    variables = {
      SAGEMAKER_ROLE_ARN = aws_iam_role.sagemaker_role.arn
      ECR_URI            = aws_ecr_repository.thai_ocr_repo.repository_url
      S3_BUCKET          = aws_s3_bucket.thai_ocr_bucket.bucket
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda-start-training-role-${var.environment}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      { Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" }}
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_sagemaker" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}
```

## Usage

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Plan changes:
   ```bash
   terraform plan -var "project_id=001"
   ```

3. Apply:
   ```bash
   terraform apply -var "project_id=001" -auto-approve
   ```
