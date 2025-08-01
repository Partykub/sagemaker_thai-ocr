#!/usr/bin/env python3
"""
Upload Training Data to S3 for SageMaker
"""

import os
import boto3
import logging
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )
    return logging.getLogger(__name__)

def get_s3_bucket_name():
    """Get S3 bucket name from Terraform outputs"""
    try:
        import subprocess
        import json
        
        result = subprocess.run(
            ['terraform', 'output', '-json'],
            cwd='terraform',
            capture_output=True,
            text=True,
            check=True
        )
        
        outputs = json.loads(result.stdout)
        bucket_name = outputs['s3_bucket_name']['value']
        
        logger = logging.getLogger(__name__)
        logger.info(f"Found S3 bucket: {bucket_name}")
        
        return bucket_name
        
    except Exception as e:
        raise Exception(f"Failed to get S3 bucket name from Terraform: {e}")

def upload_file_to_s3(file_path, bucket_name, s3_key):
    """Upload a file to S3"""
    s3_client = boto3.client('s3')
    logger = logging.getLogger(__name__)
    
    try:
        s3_client.upload_file(file_path, bucket_name, s3_key)
        logger.info(f"✅ Uploaded: {file_path} → s3://{bucket_name}/{s3_key}")
        return True
    except ClientError as e:
        logger.error(f"❌ Failed to upload {file_path}: {e}")
        return False

def upload_directory_to_s3(local_dir, bucket_name, s3_prefix):
    """Upload entire directory to S3"""
    logger = logging.getLogger(__name__)
    local_path = Path(local_dir)
    
    if not local_path.exists():
        raise FileNotFoundError(f"Local directory not found: {local_dir}")
    
    success_count = 0
    total_count = 0
    
    # Upload all files in directory
    for file_path in local_path.rglob('*'):
        if file_path.is_file():
            # Calculate relative path for S3 key
            relative_path = file_path.relative_to(local_path)
            s3_key = f"{s3_prefix}/{relative_path}".replace('\\', '/')
            
            total_count += 1
            if upload_file_to_s3(str(file_path), bucket_name, s3_key):
                success_count += 1
    
    logger.info(f"Upload summary: {success_count}/{total_count} files uploaded successfully")
    return success_count == total_count

def main():
    """Main function to upload training data"""
    logger = setup_logging()
    logger.info("Starting data upload to S3 for SageMaker training")
    
    try:
        # Get S3 bucket name
        bucket_name = get_s3_bucket_name()
        
        # Define source data directory
        data_dir = Path("thai-letters/datasets/converted/train_data_thai_paddleocr_0731_1604/train_data")
        
        if not data_dir.exists():
            raise FileNotFoundError(f"Training data directory not found: {data_dir}")
        
        logger.info(f"Uploading data from: {data_dir}")
        
        # Upload training data
        if upload_directory_to_s3(str(data_dir), bucket_name, "data/training"):
            logger.info("🎉 All training data uploaded successfully!")
            
            # Show S3 URLs
            logger.info(f"📍 Training data location: s3://{bucket_name}/data/training/")
            logger.info(f"📍 Config file: s3://{bucket_name}/data/training/th_dict.txt")
            logger.info(f"📍 Train labels: s3://{bucket_name}/data/training/rec/rec_gt_train.txt")
            logger.info(f"📍 Val labels: s3://{bucket_name}/data/training/rec/rec_gt_val.txt")
            
        else:
            logger.error("❌ Some files failed to upload")
            return False
            
    except NoCredentialsError:
        logger.error("❌ AWS credentials not found. Please configure AWS CLI.")
        return False
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
