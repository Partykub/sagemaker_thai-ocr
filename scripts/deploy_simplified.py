#!/usr/bin/env python3
"""
Simplified SageMaker Deployment Script
Uses existing AWS resources and limited permissions
"""

import os
import sys
import boto3
import json
import logging
import subprocess
import time
import base64
from pathlib import Path
from botocore.exceptions import ClientError

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )
    return logging.getLogger(__name__)

def get_existing_resources():
    """Get existing AWS resources"""
    logger = logging.getLogger(__name__)
    
    try:
        # Get S3 bucket
        s3_client = boto3.client('s3')
        buckets = s3_client.list_buckets()
        
        paddleocr_buckets = [b['Name'] for b in buckets['Buckets'] if b['Name'].startswith('paddleocr-')]
        
        if not paddleocr_buckets:
            logger.error("❌ No S3 bucket starting with 'paddleocr-' found")
            return None
        
        bucket_name = paddleocr_buckets[0]
        logger.info(f"✅ Found S3 bucket: {bucket_name}")
        
        # Get ECR repository
        ecr_client = boto3.client('ecr')
        repos = ecr_client.describe_repositories()
        
        paddleocr_repos = [r for r in repos['repositories'] if 'paddleocr' in r['repositoryName']]
        
        if not paddleocr_repos:
            logger.error("❌ No ECR repository with 'paddleocr' found")
            return None
        
        repo = paddleocr_repos[0]
        repo_url = repo['repositoryUri']
        logger.info(f"✅ Found ECR repository: {repo_url}")
        
        # Get IAM role
        iam_client = boto3.client('iam')
        roles = iam_client.list_roles()
        
        paddleocr_roles = [r for r in roles['Roles'] if 'paddleocr' in r['RoleName'] and 'sagemaker' in r['RoleName']]
        
        if not paddleocr_roles:
            logger.error("❌ No SageMaker IAM role with 'paddleocr' found")
            return None
        
        role = paddleocr_roles[0]
        role_arn = role['Arn']
        logger.info(f"✅ Found IAM role: {role_arn}")
        
        return {
            'bucket_name': bucket_name,
            'ecr_url': repo_url,
            'role_arn': role_arn
        }
        
    except ClientError as e:
        logger.error(f"❌ Failed to get AWS resources: {e}")
        return None

def upload_training_data(bucket_name):
    """Upload training data to S3"""
    logger = logging.getLogger(__name__)
    logger.info("📤 Uploading training data to S3...")
    
    s3_client = boto3.client('s3')
    data_dir = Path("thai-letters/datasets/converted/train_data_thai_paddleocr_0731_1604/train_data")
    
    if not data_dir.exists():
        logger.error(f"❌ Training data directory not found: {data_dir}")
        return False
    
    success_count = 0
    total_count = 0
    
    for file_path in data_dir.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(data_dir)
            s3_key = f"data/training/{relative_path}".replace('\\', '/')
            
            try:
                s3_client.upload_file(str(file_path), bucket_name, s3_key)
                success_count += 1
                if success_count % 100 == 0:
                    logger.info(f"   Uploaded {success_count} files...")
            except ClientError as e:
                logger.error(f"❌ Failed to upload {file_path}: {e}")
            
            total_count += 1
    
    logger.info(f"✅ Upload complete: {success_count}/{total_count} files")
    return success_count == total_count

def build_and_push_docker(ecr_url):
    """Build and push Docker image"""
    logger = logging.getLogger(__name__)
    logger.info("🐳 Building and pushing Docker image...")
    
    try:
        # Get ECR login
        region = ecr_url.split('.')[3]  # Extract region from URL
        
        ecr_client = boto3.client('ecr', region_name=region)
        token = ecr_client.get_authorization_token()
        
        auth_data = token['authorizationData'][0]
        username, password = base64.b64decode(auth_data['authorizationToken']).decode('utf-8').split(':')
        registry = auth_data['proxyEndpoint']
        
        # Docker login
        login_cmd = f'echo {password} | docker login --username {username} --password-stdin {registry}'
        result = subprocess.run(login_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Docker login failed: {result.stderr}")
            return False
        
        logger.info("✅ Docker login successful")
        
        # Build image
        build_cmd = ['docker', 'build', '-f', 'Dockerfile.sagemaker', '-t', 'thai-ocr-sagemaker:latest', '.']
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Docker build failed: {result.stderr}")
            return False
        
        logger.info("✅ Docker build successful")
        
        # Tag and push
        tag_cmd = ['docker', 'tag', 'thai-ocr-sagemaker:latest', f'{ecr_url}:latest']
        result = subprocess.run(tag_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Docker tag failed: {result.stderr}")
            return False
        
        push_cmd = ['docker', 'push', f'{ecr_url}:latest']
        result = subprocess.run(push_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Docker push failed: {result.stderr}")
            return False
        
        logger.info("✅ Docker push successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Docker build/push failed: {e}")
        return False

def create_training_job(bucket_name, ecr_url, role_arn):
    """Create SageMaker training job"""
    logger = logging.getLogger(__name__)
    logger.info("🚀 Creating SageMaker training job...")
    
    sagemaker_client = boto3.client('sagemaker')
    
    job_name = f"paddleocr-thai-training-{int(time.time())}"
    
    training_job_config = {
        'TrainingJobName': job_name,
        'RoleArn': role_arn,
        'AlgorithmSpecification': {
            'TrainingImage': f'{ecr_url}:latest',
            'TrainingInputMode': 'File'
        },
        'InputDataConfig': [
            {
                'ChannelName': 'training',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': f's3://{bucket_name}/data/training/',
                        'S3DataDistribution': 'FullyReplicated'
                    }
                },
                'ContentType': 'application/x-parquet',
                'CompressionType': 'None'
            }
        ],
        'OutputDataConfig': {
            'S3OutputPath': f's3://{bucket_name}/models/'
        },
        'ResourceConfig': {
            'InstanceType': 'ml.m5.large',
            'InstanceCount': 1,
            'VolumeSizeInGB': 30
        },
        'StoppingCondition': {
            'MaxRuntimeInSeconds': 86400  # 24 hours
        },
        'HyperParameters': {
            'epochs': '100',
            'batch-size': '128',
            'learning-rate': '0.001',
            'use-gpu': 'false'  # ml.m5.large is CPU only
        }
    }
    
    try:
        response = sagemaker_client.create_training_job(**training_job_config)
        logger.info(f"✅ Training job created: {job_name}")
        logger.info(f"📍 Training job ARN: {response['TrainingJobArn']}")
        
        return job_name
        
    except ClientError as e:
        logger.error(f"❌ Failed to create training job: {e}")
        return None

def monitor_training_job(job_name):
    """Monitor training job status"""
    logger = logging.getLogger(__name__)
    logger.info(f"📊 Monitoring training job: {job_name}")
    
    sagemaker_client = boto3.client('sagemaker')
    
    try:
        response = sagemaker_client.describe_training_job(TrainingJobName=job_name)
        status = response['TrainingJobStatus']
        
        logger.info(f"📍 Training job status: {status}")
        
        if status in ['InProgress', 'Stopping']:
            logger.info("⏳ Training is in progress...")
            logger.info("💡 Monitor progress with:")
            logger.info(f"   aws sagemaker describe-training-job --training-job-name {job_name}")
            logger.info(f"   aws logs tail /aws/sagemaker/TrainingJobs --follow")
        
        elif status == 'Completed':
            logger.info("🎉 Training completed successfully!")
            logger.info(f"📁 Model artifacts: s3://{response['OutputDataConfig']['S3OutputPath']}")
        
        elif status == 'Failed':
            logger.error("❌ Training failed")
            if 'FailureReason' in response:
                logger.error(f"   Reason: {response['FailureReason']}")
        
        return status
        
    except ClientError as e:
        logger.error(f"❌ Failed to describe training job: {e}")
        return None

def main():
    """Main deployment function"""
    logger = setup_logging()
    logger.info("🎯 Starting Simplified SageMaker Deployment")
    
    # Check prerequisites
    required_files = [
        'thai-letters/datasets/converted/train_data_thai_paddleocr_0731_1604/train_data/th_dict.txt',
        'configs/rec/thai_rec_sagemaker.yml',
        'Dockerfile.sagemaker'
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            logger.error(f"❌ Required file not found: {file_path}")
            return False
    
    # Get existing AWS resources
    resources = get_existing_resources()
    if not resources:
        logger.error("❌ Failed to find required AWS resources")
        return False
    
    # Upload training data
    if not upload_training_data(resources['bucket_name']):
        logger.error("❌ Failed to upload training data")
        return False
    
    # Build and push Docker image
    if not build_and_push_docker(resources['ecr_url']):
        logger.error("❌ Failed to build/push Docker image")
        return False
    
    # Create training job
    job_name = create_training_job(
        resources['bucket_name'],
        resources['ecr_url'], 
        resources['role_arn']
    )
    
    if not job_name:
        logger.error("❌ Failed to create training job")
        return False
    
    # Monitor initial status
    monitor_training_job(job_name)
    
    logger.info("🎉 Deployment completed successfully!")
    logger.info("📊 Summary:")
    logger.info(f"   ✅ S3 bucket: {resources['bucket_name']}")
    logger.info(f"   ✅ ECR image: {resources['ecr_url']}:latest")
    logger.info(f"   ✅ Training job: {job_name}")
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
