#!/usr/bin/env python3
"""
AWS SageMaker Training Script for Thai OCR
Uses permissions defined in required_permissions.json
"""

import boto3
import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ThaiOCRSageMakerTrainer:
    def __init__(self, region_name: str = "ap-southeast-1"):
        """Initialize SageMaker trainer with limited permissions."""
        self.region = region_name
        self.sagemaker = boto3.client('sagemaker', region_name=region_name)
        self.s3 = boto3.client('s3', region_name=region_name)
        self.ecr = boto3.client('ecr', region_name=region_name)
        
        # Configuration based on permissions
        self.bucket_prefix = "paddleocr"
        self.role_prefix = "paddleocr"
        self.repo_prefix = "paddleocr"
        
    def create_training_job(
        self,
        job_name: str,
        role_arn: str,
        image_uri: str,
        s3_input_path: str,
        s3_output_path: str,
        instance_type: str = "ml.m5.large",
        instance_count: int = 1,
        max_runtime_in_seconds: int = 86400,  # 24 hours
        hyperparameters: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Create SageMaker training job with available permissions.
        """
        try:
            if hyperparameters is None:
                hyperparameters = {
                    'epochs': '100',
                    'batch_size': '32',
                    'learning_rate': '0.001'
                }
            
            training_params = {
                'TrainingJobName': job_name,
                'RoleArn': role_arn,
                'AlgorithmSpecification': {
                    'TrainingImage': image_uri,
                    'TrainingInputMode': 'File'
                },
                'InputDataConfig': [
                    {
                        'ChannelName': 'training',
                        'DataSource': {
                            'S3DataSource': {
                                'S3DataType': 'S3Prefix',
                                'S3Uri': s3_input_path,
                                'S3DataDistributionType': 'FullyReplicated'
                            }
                        },
                        'ContentType': 'application/x-parquet',
                        'CompressionType': 'None'
                    }
                ],
                'OutputDataConfig': {
                    'S3OutputPath': s3_output_path
                },
                'ResourceConfig': {
                    'InstanceType': instance_type,
                    'InstanceCount': instance_count,
                    'VolumeSizeInGB': 30
                },
                'StoppingCondition': {
                    'MaxRuntimeInSeconds': max_runtime_in_seconds
                },
                'HyperParameters': hyperparameters
            }
            
            response = self.sagemaker.create_training_job(**training_params)
            logger.info(f"Training job created successfully: {job_name}")
            logger.info(f"Training job ARN: {response['TrainingJobArn']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create training job: {e}")
            return False
    
    def describe_training_job(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Get training job status and details."""
        try:
            response = self.sagemaker.describe_training_job(TrainingJobName=job_name)
            return response
        except Exception as e:
            logger.error(f"Failed to describe training job {job_name}: {e}")
            return None
    
    def list_training_jobs(self, max_results: int = 10) -> Optional[Dict[str, Any]]:
        """List recent training jobs."""
        try:
            response = self.sagemaker.list_training_jobs(
                SortBy='CreationTime',
                SortOrder='Descending',
                MaxResults=max_results
            )
            return response
        except Exception as e:
            logger.error(f"Failed to list training jobs: {e}")
            return None
    
    def create_model(
        self,
        model_name: str,
        role_arn: str,
        image_uri: str,
        model_data_url: str
    ) -> bool:
        """Create SageMaker model for inference."""
        try:
            model_params = {
                'ModelName': model_name,
                'ExecutionRoleArn': role_arn,
                'PrimaryContainer': {
                    'Image': image_uri,
                    'ModelDataUrl': model_data_url
                }
            }
            
            response = self.sagemaker.create_model(**model_params)
            logger.info(f"Model created successfully: {model_name}")
            logger.info(f"Model ARN: {response['ModelArn']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create model: {e}")
            return False
    
    def wait_for_training_job(self, job_name: str, check_interval: int = 60) -> str:
        """Wait for training job to complete."""
        logger.info(f"Waiting for training job {job_name} to complete...")
        
        while True:
            job_info = self.describe_training_job(job_name)
            if not job_info:
                return "Failed"
            
            status = job_info['TrainingJobStatus']
            logger.info(f"Training job status: {status}")
            
            if status in ['Completed', 'Failed', 'Stopped']:
                if status == 'Completed':
                    logger.info("Training job completed successfully!")
                else:
                    logger.error(f"Training job ended with status: {status}")
                    if 'FailureReason' in job_info:
                        logger.error(f"Failure reason: {job_info['FailureReason']}")
                return status
            
            time.sleep(check_interval)

def main():
    """Main function to demonstrate usage."""
    trainer = ThaiOCRSageMakerTrainer()
    
    # Example usage
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    job_name = f"paddleocr-thai-training-{timestamp}"
    
    # These would be set based on your actual resources
    role_arn = "arn:aws:iam::484468818942:role/paddleocr-dev-sagemaker-role"
    image_uri = "484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:latest"
    s3_input = "s3://paddleocr-dev-data-xxxxx/data/training/"
    s3_output = "s3://paddleocr-dev-data-xxxxx/models/"
    
    # Create training job
    success = trainer.create_training_job(
        job_name=job_name,
        role_arn=role_arn,
        image_uri=image_uri,
        s3_input_path=s3_input,
        s3_output_path=s3_output,
        instance_type="ml.m5.large",
        instance_count=1
    )
    
    if success:
        # Wait for completion
        final_status = trainer.wait_for_training_job(job_name)
        logger.info(f"Training job final status: {final_status}")
    
    # List recent jobs
    recent_jobs = trainer.list_training_jobs()
    if recent_jobs:
        logger.info("Recent training jobs:")
        for job in recent_jobs['TrainingJobSummaries']:
            logger.info(f"  {job['TrainingJobName']}: {job['TrainingJobStatus']}")

if __name__ == "__main__":
    main()
