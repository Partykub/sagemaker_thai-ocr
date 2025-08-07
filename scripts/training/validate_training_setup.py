#!/usr/bin/env python3
"""
Pre-training Validator for SageMaker Numbers OCR
ตรวจสอบความพร้อมของระบบก่อนเริ่มการเทรน
"""

import boto3
import json
import os
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = 'ap-southeast-1'
ACCOUNT_ID = '484468818942'
ECR_REPO = 'paddleocr-dev'
ECR_IMAGE_TAG = 'numbers-latest'
S3_BUCKET = 'paddleocr-dev-data-bucket'
SAGEMAKER_ROLE = 'paddleocr-dev-sagemaker-role'

def check_aws_credentials():
    """ตรวจสอบ AWS credentials"""
    try:
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        
        account = identity['Account']
        user_arn = identity['Arn']
        
        logger.info(f"✅ AWS Credentials OK")
        logger.info(f"   Account: {account}")
        logger.info(f"   User: {user_arn}")
        
        if account != ACCOUNT_ID:
            logger.warning(f"⚠️ Account mismatch! Expected: {ACCOUNT_ID}, Got: {account}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ AWS Credentials failed: {str(e)}")
        return False

def check_ecr_image():
    """ตรวจสอบ ECR image"""
    try:
        ecr_client = boto3.client('ecr', region_name=AWS_REGION)
        
        # List images in repository
        response = ecr_client.describe_images(
            repositoryName=ECR_REPO,
            imageIds=[{'imageTag': ECR_IMAGE_TAG}]
        )
        
        if not response['imageDetails']:
            logger.error(f"❌ Image {ECR_IMAGE_TAG} not found in ECR")
            return False
        
        image_details = response['imageDetails'][0]
        image_size_mb = image_details['imageSizeInBytes'] / (1024 * 1024)
        pushed_at = image_details['imagePushedAt']
        
        logger.info(f"✅ ECR Image OK")
        logger.info(f"   Repository: {ECR_REPO}")
        logger.info(f"   Tag: {ECR_IMAGE_TAG}")
        logger.info(f"   Size: {image_size_mb:.1f} MB")
        logger.info(f"   Pushed: {pushed_at}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ECR Image check failed: {str(e)}")
        return False

def check_s3_data():
    """ตรวจสอบข้อมูลใน S3"""
    try:
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        
        # Check bucket existence
        s3_client.head_bucket(Bucket=S3_BUCKET)
        logger.info(f"✅ S3 Bucket exists: {S3_BUCKET}")
        
        # Check training data
        training_prefix = 'data/training/'
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix=training_prefix
        )
        
        if 'Contents' not in response:
            logger.error(f"❌ No training data found in s3://{S3_BUCKET}/{training_prefix}")
            return False
        
        total_objects = len(response['Contents'])
        total_size = sum([obj['Size'] for obj in response['Contents']])
        total_size_mb = total_size / (1024 * 1024)
        
        logger.info(f"✅ Training Data OK")
        logger.info(f"   Objects: {total_objects}")
        logger.info(f"   Total Size: {total_size_mb:.1f} MB")
        
        # Show sample files
        logger.info("   Sample files:")
        for obj in response['Contents'][:5]:
            key = obj['Key']
            size_kb = obj['Size'] / 1024
            logger.info(f"     - {key} ({size_kb:.1f} KB)")
        
        if total_objects > 5:
            logger.info(f"     ... and {total_objects - 5} more files")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ S3 Data check failed: {str(e)}")
        return False

def check_sagemaker_role():
    """ตรวจสอบ SageMaker IAM role"""
    try:
        iam_client = boto3.client('iam', region_name=AWS_REGION)
        
        # Get role details
        response = iam_client.get_role(RoleName=SAGEMAKER_ROLE)
        role_arn = response['Role']['Arn']
        
        logger.info(f"✅ SageMaker Role OK")
        logger.info(f"   Role ARN: {role_arn}")
        
        # Check attached policies
        policies_response = iam_client.list_attached_role_policies(RoleName=SAGEMAKER_ROLE)
        attached_policies = [p['PolicyName'] for p in policies_response['AttachedPolicies']]
        
        logger.info(f"   Attached Policies: {', '.join(attached_policies)}")
        
        # Check for required SageMaker permissions
        required_policies = ['AmazonSageMakerFullAccess', 'AmazonS3FullAccess']
        missing_policies = [p for p in required_policies if p not in attached_policies]
        
        if missing_policies:
            logger.warning(f"⚠️ Missing recommended policies: {', '.join(missing_policies)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SageMaker Role check failed: {str(e)}")
        return False

def check_local_config():
    """ตรวจสอบไฟล์ config ในเครื่อง"""
    try:
        config_path = Path("configs/rec/numbers_config.yml")
        
        if not config_path.exists():
            logger.error(f"❌ Config file not found: {config_path}")
            return False
        
        logger.info(f"✅ Config File OK")
        logger.info(f"   Path: {config_path}")
        logger.info(f"   Size: {config_path.stat().st_size} bytes")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Local Config check failed: {str(e)}")
        return False

def estimate_training_cost():
    """ประมาณการค่าใช้จ่าย"""
    logger.info("💰 Training Cost Estimation")
    logger.info("   Instance Type: ml.g4dn.xlarge (GPU)")
    logger.info("   Hourly Rate: ~$0.526 USD")
    logger.info("   Expected Training Time: 30-60 minutes")
    logger.info("   Estimated Cost: $0.26 - $0.53 USD")

def main():
    """Main validation function"""
    
    logger.info("🔍 Pre-Training Validation for Thai Numbers OCR")
    logger.info("=" * 60)
    
    checks = [
        ("AWS Credentials", check_aws_credentials),
        ("ECR Docker Image", check_ecr_image),
        ("S3 Training Data", check_s3_data),
        ("SageMaker IAM Role", check_sagemaker_role),
        ("Local Configuration", check_local_config)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        logger.info(f"\n🔄 Checking {check_name}...")
        if not check_func():
            all_passed = False
    
    logger.info("\n" + "=" * 60)
    
    if all_passed:
        logger.info("🎉 All checks passed! Ready for training!")
        logger.info("\n💡 To start training, run:")
        logger.info("   python scripts/training/manual_numbers_training.py")
        logger.info("")
        estimate_training_cost()
    else:
        logger.error("❌ Some checks failed. Please fix the issues above.")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    exit(main())
