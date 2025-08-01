#!/usr/bin/env python3
"""
Continue Deployment: Docker build and SageMaker training only
(Skip data upload since it's already done)
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
        bucket_name = paddleocr_buckets[0]
        logger.info(f"✅ Found S3 bucket: {bucket_name}")
        
        # Get ECR repository
        ecr_client = boto3.client('ecr')
        repos = ecr_client.describe_repositories()
        
        paddleocr_repos = [r for r in repos['repositories'] if 'paddleocr' in r['repositoryName']]
        repo = paddleocr_repos[0]
        repo_url = repo['repositoryUri']
        logger.info(f"✅ Found ECR repository: {repo_url}")
        
        # Get IAM role
        iam_client = boto3.client('iam')
        roles = iam_client.list_roles()
        
        paddleocr_roles = [r for r in roles['Roles'] if 'paddleocr' in r['RoleName'] and 'sagemaker' in r['RoleName']]
        role = paddleocr_roles[0]
        role_arn = role['Arn']
        logger.info(f"✅ Found IAM role: {role_arn}")
        
        return {
            'bucket_name': bucket_name,
            'ecr_url': repo_url,
            'role_arn': role_arn
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get AWS resources: {e}")
        return None

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
        
        # Use Popen for real-time output with proper encoding
        logger.info("🔨 Building Docker image...")
        with subprocess.Popen(
            build_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='ignore',
            bufsize=1,
            universal_newlines=True
        ) as proc:
            for line in proc.stdout:
                if line.strip():
                    logger.info(f"Docker: {line.strip()}")
            
            proc.wait()
            if proc.returncode != 0:
                logger.error(f"❌ Docker build failed with return code: {proc.returncode}")
                return False
        
        logger.info("✅ Docker build successful")
        
        # Tag image for ECR
        tag_cmd = f'docker tag thai-ocr-sagemaker:latest {ecr_url}:latest'
        result = subprocess.run(tag_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Docker tag failed: {result.stderr}")
            return False
        
        # Push image
        push_cmd = f'docker push {ecr_url}:latest'
        result = subprocess.run(push_cmd, shell=True, capture_output=True, text=True)
        
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
                        'S3DataDistributionType': 'FullyReplicated'
                    }
                },
                'ContentType': 'application/json',
                'CompressionType': 'None'
            }
        ],
        'OutputDataConfig': {
            'S3OutputPath': f's3://{bucket_name}/output/'
        },
        'ResourceConfig': {
            'InstanceType': 'ml.m5.large',
            'InstanceCount': 1,
            'VolumeSizeInGB': 30
        },
        'StoppingCondition': {
            'MaxRuntimeInSeconds': 86400  # 24 hours
        }
    }
    
    try:
        response = sagemaker_client.create_training_job(**training_job_config)
        logger.info(f"✅ Training job created: {job_name}")
        logger.info(f"📊 Job ARN: {response.get('TrainingJobArn', 'N/A')}")
        return job_name
        
    except Exception as e:
        logger.error(f"❌ Failed to create training job: {e}")
        return None

def main():
    """Main deployment function"""
    logger = setup_logging()
    logger.info("🎯 Continue Deployment: Docker + SageMaker Training")
    
    # Get existing AWS resources
    resources = get_existing_resources()
    if not resources:
        logger.error("❌ Failed to get AWS resources")
        return False
    
    bucket_name = resources['bucket_name']
    ecr_url = resources['ecr_url']
    role_arn = resources['role_arn']
    
    # Build and push Docker image
    if not build_and_push_docker(ecr_url):
        logger.error("❌ Failed to build/push Docker image")
        return False
    
    # Create SageMaker training job
    job_name = create_training_job(bucket_name, ecr_url, role_arn)
    if not job_name:
        logger.error("❌ Failed to create training job")
        return False
    
    logger.info("🎉 Deployment completed successfully!")
    logger.info(f"📝 Training job: {job_name}")
    logger.info("🔍 Monitor progress in AWS SageMaker console")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
