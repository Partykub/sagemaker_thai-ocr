#!/usr/bin/env python3
"""
Create SageMaker Training Job using AWS CLI
Since Terraform doesn't support aws_sagemaker_training_job directly
"""

import os
import boto3
import json
import subprocess
import logging
from datetime import datetime

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )
    return logging.getLogger(__name__)

def get_terraform_outputs():
    """Get outputs from Terraform"""
    try:
        result = subprocess.run(
            ['terraform', 'output', '-json'],
            cwd='terraform',
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        
        return json.loads(result.stdout)
        
    except Exception as e:
        raise Exception(f"Failed to get Terraform outputs: {e}")

def create_training_job(outputs, hyperparameters):
    """Create SageMaker training job"""
    logger = logging.getLogger(__name__)
    
    # Generate unique job name
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    job_name = f"paddleocr-dev-training-{timestamp}"
    
    # Get values from Terraform outputs
    s3_bucket = outputs['s3_bucket_name']['value']
    ecr_repo_url = outputs['ecr_repository_url']['value']
    role_arn = outputs['sagemaker_execution_role_arn']['value']
    
    # SageMaker client
    sagemaker = boto3.client('sagemaker')
    
    # Training job configuration
    training_job_config = {
        'TrainingJobName': job_name,
        'RoleArn': role_arn,
        'AlgorithmSpecification': {
            'TrainingImage': f"{ecr_repo_url}:latest",
            'TrainingInputMode': 'File'
        },
        'InputDataConfig': [
            {
                'ChannelName': 'training',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': f's3://{s3_bucket}/data/training/',
                        'S3DataDistributionType': 'FullyReplicated'
                    }
                },
                'ContentType': 'application/x-octet-stream',
                'CompressionType': 'None'
            }
        ],
        'OutputDataConfig': {
            'S3OutputPath': f's3://{s3_bucket}/models/'
        },
        'ResourceConfig': {
            'InstanceType': hyperparameters.get('training_instance_type', 'ml.m5.large'),
            'InstanceCount': 1,
            'VolumeSizeInGB': 30
        },
        'StoppingCondition': {
            'MaxRuntimeInSeconds': hyperparameters.get('max_training_time', 86400)
        },
        'HyperParameters': {
            'epochs': str(hyperparameters.get('training_epochs', 100)),
            'batch-size': str(hyperparameters.get('training_batch_size', 128)),
            'learning-rate': str(hyperparameters.get('training_learning_rate', 0.001)),
            'use-gpu': str(hyperparameters.get('use_gpu', True)).lower()
        },
        'Tags': [
            {'Key': 'Project', 'Value': 'paddleocr'},
            {'Key': 'Environment', 'Value': 'dev'},
            {'Key': 'Owner', 'Value': 'partykub'}
        ]
    }
    
    try:
        logger.info(f"Creating SageMaker training job: {job_name}")
        
        response = sagemaker.create_training_job(**training_job_config)
        
        logger.info(f"✅ Training job created successfully!")
        logger.info(f"📍 Job Name: {job_name}")
        logger.info(f"📍 Job ARN: {response['TrainingJobArn']}")
        logger.info(f"📍 S3 Input: s3://{s3_bucket}/data/training/")
        logger.info(f"📍 S3 Output: s3://{s3_bucket}/models/")
        logger.info(f"📍 Docker Image: {ecr_repo_url}:latest")
        
        return job_name
        
    except Exception as e:
        logger.error(f"❌ Failed to create training job: {e}")
        raise

def main():
    """Main function"""
    logger = setup_logging()
    logger.info("🚀 Creating SageMaker training job")
    
    try:
        # Get Terraform outputs
        outputs = get_terraform_outputs()
        
        # Default hyperparameters (can be overridden by Terraform variables)
        hyperparameters = {
            'training_instance_type': 'ml.m5.large',
            'training_epochs': 100,
            'training_batch_size': 128,
            'training_learning_rate': 0.001,
            'max_training_time': 86400,
            'use_gpu': False  # Set to True for GPU instances
        }
        
        # Create training job
        job_name = create_training_job(outputs, hyperparameters)
        
        logger.info("🎉 SageMaker training job created successfully!")
        logger.info("📊 Next steps:")
        logger.info(f"   1. Monitor job: aws sagemaker describe-training-job --training-job-name {job_name}")
        logger.info("   2. View logs: aws logs tail /aws/sagemaker/TrainingJobs --follow")
        logger.info("   3. Check AWS Console: SageMaker → Training jobs")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create training job: {e}")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
