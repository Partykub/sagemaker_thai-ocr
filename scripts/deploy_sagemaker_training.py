#!/usr/bin/env python3
"""
Master Deployment Script for SageMaker Thai OCR Training
This script orchestrates the entire deployment process:
1. Upload training data to S3
2. Build and push Docker image to ECR
3. Deploy SageMaker training job with Terraform
"""

import os
import sys
import subprocess
import logging
import time
from pathlib import Path

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )
    return logging.getLogger(__name__)

def run_script(script_path, description):
    """Run a Python script and return success status"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"🚀 {description}")
    
    try:
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
        
        logger.info(f"✅ {description} completed successfully")
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed")
        logger.error(f"Error: {e.stderr}")
        return False

def run_terraform_command(command, description):
    """Run Terraform command"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"🚀 {description}")
    
    try:
        result = subprocess.run(
            command.split(),
            cwd='terraform',
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        
        logger.info(f"✅ {description} completed successfully")
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed")
        logger.error(f"Error: {e.stderr}")
        return False

def main():
    """Main deployment function"""
    logger = setup_logging()
    logger.info("🎯 Starting SageMaker Thai OCR Deployment")
    
    # Check prerequisites
    required_files = [
        'terraform/terraform.tfvars',
        'thai-letters/datasets/converted/train_data_thai_paddleocr_0731_1604/train_data/th_dict.txt',
        'configs/rec/thai_rec_sagemaker.yml',
        'Dockerfile.sagemaker'
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            logger.error(f"❌ Required file not found: {file_path}")
            if file_path == 'terraform/terraform.tfvars':
                logger.info("📝 Please copy terraform.tfvars.example to terraform.tfvars and configure it")
            return False
    
    logger.info("✅ All prerequisites found")
    
    # Step 1: Initialize Terraform (if needed)
    if not Path('terraform/.terraform').exists():
        if not run_terraform_command('terraform init', 'Initializing Terraform'):
            return False
    
    # Step 2: Plan and apply Terraform infrastructure
    if not run_terraform_command('terraform plan', 'Planning Terraform infrastructure'):
        return False
    
    if not run_terraform_command('terraform apply -auto-approve', 'Creating AWS infrastructure'):
        return False
    
    # Step 3: Upload training data to S3
    if not run_script('scripts/utils/upload_data_to_s3.py', 'Uploading training data to S3'):
        return False
    
    # Step 4: Build and push Docker image
    if not run_script('scripts/utils/build_and_push_docker.py', 'Building and pushing Docker image'):
        return False
    
    # Step 5: Create SageMaker training job
    if not run_script('scripts/utils/create_sagemaker_training_job.py', 'Creating SageMaker training job'):
        return False
    
    # Step 6: Show deployment summary
    logger.info("🎉 Deployment completed successfully!")
    logger.info("📊 Summary:")
    logger.info("   ✅ AWS infrastructure created")
    logger.info("   ✅ Training data uploaded to S3")
    logger.info("   ✅ Docker image built and pushed to ECR")
    logger.info("   ✅ SageMaker training job started")
    
    logger.info("📍 Next steps:")
    logger.info("   1. Monitor training job in AWS Console")
    logger.info("   2. Check CloudWatch logs for training progress")
    logger.info("   3. Download trained model from S3 when complete")
    
    logger.info("🔧 Useful commands:")
    logger.info("   - Check training status: aws sagemaker describe-training-job --training-job-name <job-name>")
    logger.info("   - View logs: aws logs tail /aws/sagemaker/TrainingJobs --follow")
    logger.info("   - Clean up: terraform destroy")
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
