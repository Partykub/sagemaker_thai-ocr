#!/usr/bin/env python3
"""
Manual SageMaker Training Job Creator for Thai Numbers OCR
สำหรับการเทรนตัวเลข 0-9 บน AWS SageMaker
"""

import boto3
import json
import time
from datetime import datetime
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
ECR_IMAGE_URI = f'{ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/paddleocr-dev:numbers-latest'
SAGEMAKER_ROLE_ARN = f'arn:aws:iam::{ACCOUNT_ID}:role/paddleocr-dev-sagemaker-role'
S3_INPUT_PATH = 's3://paddleocr-dev-data-bucket/data/training/'
S3_OUTPUT_PATH = 's3://paddleocr-dev-data-bucket/models/'

def create_training_job():
    """สร้าง SageMaker training job สำหรับตัวเลข"""
    
    # สร้าง SageMaker client
    sagemaker_client = boto3.client('sagemaker', region_name=AWS_REGION)
    
    # สร้าง training job name ด้วย timestamp
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    training_job_name = f'thai-numbers-ocr-{timestamp}'
    
    logger.info(f"🎯 Creating training job: {training_job_name}")
    
    # Training job configuration
    training_config = {
        'TrainingJobName': training_job_name,
        'AlgorithmSpecification': {
            'TrainingImage': ECR_IMAGE_URI,
            'TrainingInputMode': 'File'
        },
        'RoleArn': SAGEMAKER_ROLE_ARN,
        'InputDataConfig': [
            {
                'ChannelName': 'training',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': S3_INPUT_PATH,
                        'S3DataDistributionType': 'FullyReplicated'
                    }
                },
                'ContentType': 'application/json',
                'CompressionType': 'None'
            }
        ],
        'OutputDataConfig': {
            'S3OutputPath': S3_OUTPUT_PATH
        },
        'ResourceConfig': {
            'InstanceType': 'ml.g4dn.xlarge',  # GPU instance เหมาะกับ deep learning
            'InstanceCount': 1,
            'VolumeSizeInGB': 30
        },
        'StoppingCondition': {
            'MaxRuntimeInSeconds': 10800  # 3 hours max
        },
        'HyperParameters': {
            'epochs': '50',
            'learning_rate': '0.005',
            'batch_size': '32',
            'config_path': 'configs/rec/numbers_config.yml'
        },
        'Tags': [
            {
                'Key': 'Project',
                'Value': 'thai-ocr-numbers'
            },
            {
                'Key': 'Environment',
                'Value': 'development'
            },
            {
                'Key': 'CreatedBy',
                'Value': 'manual-script'
            }
        ]
    }
    
    try:
        # สร้าง training job
        response = sagemaker_client.create_training_job(**training_config)
        
        logger.info("✅ Training job created successfully!")
        logger.info(f"📊 Training Job ARN: {response['TrainingJobArn']}")
        logger.info(f"🔗 Console URL: https://console.aws.amazon.com/sagemaker/home?region={AWS_REGION}#/jobs/{training_job_name}")
        
        return training_job_name, response
        
    except Exception as e:
        logger.error(f"❌ Failed to create training job: {str(e)}")
        return None, None

def monitor_training_job(job_name):
    """ติดตามสถานะของ training job"""
    
    sagemaker_client = boto3.client('sagemaker', region_name=AWS_REGION)
    
    logger.info(f"📊 Monitoring training job: {job_name}")
    logger.info("=" * 60)
    
    start_time = time.time()
    
    while True:
        try:
            response = sagemaker_client.describe_training_job(TrainingJobName=job_name)
            
            status = response['TrainingJobStatus']
            secondary_status = response.get('SecondaryStatus', 'Unknown')
            training_time = response.get('TrainingTimeInSeconds', 0)
            
            # แสดงสถานะปัจจุบัน
            current_time = datetime.now().strftime('%H:%M:%S')
            logger.info(f"[{current_time}] Status: {status} | Secondary: {secondary_status} | Time: {training_time}s")
            
            # ตรวจสอบว่า training จบแล้วหรือยัง
            if status in ['Completed', 'Failed', 'Stopped']:
                logger.info("🏁 Training finished!")
                logger.info(f"📊 Final Status: {status}")
                logger.info(f"⏱️ Total Training Time: {training_time} seconds")
                
                if 'BillableTimeInSeconds' in response:
                    billable_time = response['BillableTimeInSeconds']
                    logger.info(f"💰 Billable Time: {billable_time} seconds")
                    
                    # คำนวณค่าใช้จ่ายประมาณ (ml.g4dn.xlarge ~$0.526/hour)
                    cost_estimate = (billable_time / 3600) * 0.526
                    logger.info(f"💵 Estimated Cost: ${cost_estimate:.2f} USD")
                
                if status == 'Completed':
                    model_artifacts = response.get('ModelArtifacts', {})
                    s3_model_uri = model_artifacts.get('S3ModelArtifacts', '')
                    logger.info(f"📦 Model Artifacts: {s3_model_uri}")
                    
                elif status == 'Failed':
                    failure_reason = response.get('FailureReason', 'Unknown error')
                    logger.error(f"❌ Failure Reason: {failure_reason}")
                
                break
            
            # รอ 30 วินาทีก่อนเช็คอีกครั้ง
            time.sleep(30)
            
        except KeyboardInterrupt:
            logger.info("⚠️ Monitoring interrupted by user")
            break
        except Exception as e:
            logger.error(f"❌ Error monitoring training job: {str(e)}")
            break

def main():
    """Main function"""
    
    logger.info("🚀 Thai Numbers OCR - SageMaker Training")
    logger.info("=" * 50)
    
    # แสดงข้อมูล configuration
    logger.info(f"📍 Region: {AWS_REGION}")
    logger.info(f"🐳 ECR Image: {ECR_IMAGE_URI}")
    logger.info(f"📊 Input Data: {S3_INPUT_PATH}")
    logger.info(f"📦 Output Path: {S3_OUTPUT_PATH}")
    logger.info(f"🔧 Instance Type: ml.g4dn.xlarge (GPU)")
    logger.info("=" * 50)
    
    # สร้าง training job
    job_name, response = create_training_job()
    
    if job_name:
        logger.info("⏳ Starting training job monitoring...")
        monitor_training_job(job_name)
    else:
        logger.error("❌ Failed to create training job")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
