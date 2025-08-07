#!/usr/bin/env python3
"""
Manual SageMaker Training Job Creator for Numbers OCR
เอาไว้สร้าง training job manual เมื่อ script อัตโนมัติมีปัญหา
"""

import boto3
import time
from datetime import datetime

def create_training_job():
    """สร้าง SageMaker training job สำหรับ numbers dataset"""
    
    print("🎯 Creating SageMaker Training Job for Numbers OCR")
    
    # SageMaker client
    sagemaker = boto3.client('sagemaker', region_name='ap-southeast-1')
    
    # Job name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    job_name = f'paddleocr-numbers-training-{timestamp}'
    
    print(f"📝 Job Name: {job_name}")
    
    # Training job parameters
    training_params = {
        'TrainingJobName': job_name,
        'AlgorithmSpecification': {
            'TrainingImage': '484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:latest',
            'TrainingInputMode': 'File'
        },
        'RoleArn': 'arn:aws:iam::484468818942:role/paddleocr-dev-sagemaker-role',
        'InputDataConfig': [
            {
                'ChannelName': 'training',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': 's3://paddleocr-dev-data-bucket/data/training/',
                        'S3DataDistributionType': 'FullyReplicated'
                    }
                }
            }
        ],
        'OutputDataConfig': {
            'S3OutputPath': 's3://paddleocr-dev-data-bucket/models/'
        },
        'ResourceConfig': {
            'InstanceType': 'ml.m5.large',      # CPU instance for small dataset
            'InstanceCount': 1,
            'VolumeSizeInGB': 30
        },
        'StoppingCondition': {
            'MaxRuntimeInSeconds': 7200         # 2 hours max (should be enough for numbers)
        },
        'HyperParameters': {
            'epochs': '50',
            'learning_rate': '0.005',
            'batch_size': '32',
            'config_file': 'numbers_config.yml'
        },
        'Tags': [
            {'Key': 'Project', 'Value': 'thai-ocr'},
            {'Key': 'Dataset', 'Value': 'numbers-0-9'},
            {'Key': 'Environment', 'Value': 'development'}
        ]
    }
    
    try:
        # Create training job
        print("🚀 Creating training job...")
        response = sagemaker.create_training_job(**training_params)
        
        print(f"✅ Training job created successfully!")
        print(f"🆔 Job ARN: {response['TrainingJobArn']}")
        
        # Monitor job status
        print("📊 Monitoring training job...")
        monitor_training_job(sagemaker, job_name)
        
    except Exception as e:
        print(f"❌ Error creating training job: {e}")
        return None

def monitor_training_job(sagemaker, job_name):
    """Monitor training job progress"""
    
    print(f"👀 Monitoring job: {job_name}")
    print("=" * 60)
    
    while True:
        try:
            response = sagemaker.describe_training_job(TrainingJobName=job_name)
            
            status = response['TrainingJobStatus']
            secondary_status = response.get('SecondaryStatus', 'Unknown')
            training_time = response.get('TrainingTimeInSeconds', 0)
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] Status: {status} | Secondary: {secondary_status} | Time: {training_time}s")
            
            # Check if completed
            if status in ['Completed', 'Failed', 'Stopped']:
                print(f"\n🏁 Training {status.lower()}")
                
                if status == 'Completed':
                    print(f"✅ Training completed successfully!")
                    print(f"⏱️ Total training time: {training_time} seconds")
                    billable_time = response.get('BillableTimeInSeconds', training_time)
                    print(f"💰 Billable time: {billable_time} seconds")
                    
                    # Show model artifacts location
                    output_path = response['OutputDataConfig']['S3OutputPath']
                    print(f"📦 Model artifacts: {output_path}{job_name}/")
                    
                elif status == 'Failed':
                    failure_reason = response.get('FailureReason', 'Unknown')
                    print(f"❌ Training failed: {failure_reason}")
                
                break
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error monitoring job: {e}")
            break

if __name__ == '__main__':
    create_training_job()
