#!/usr/bin/env python3
"""
Training Job Monitor - Wait for completion and show results
"""

import boto3
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_training_completion(job_name: str) -> Dict[str, Any]:
    """Wait for training job to complete and return final status."""
    
    sagemaker = boto3.client('sagemaker')
    start_time = datetime.now()
    
    logger.info(f"🎯 Monitoring training job: {job_name}")
    logger.info("⏰ Checking status every 2 minutes...")
    
    last_status = None
    check_count = 0
    
    while True:
        try:
            response = sagemaker.describe_training_job(TrainingJobName=job_name)
            current_status = response['TrainingJobStatus']
            training_start = response.get('TrainingStartTime')
            
            check_count += 1
            elapsed = datetime.now() - start_time
            
            # Show progress if status changed or every 5 checks
            if current_status != last_status or check_count % 5 == 0:
                logger.info(f"📊 Check #{check_count:2d} | Status: {current_status} | Elapsed: {str(elapsed).split('.')[0]}")
                
                if training_start:
                    training_elapsed = datetime.now(timezone.utc) - training_start
                    logger.info(f"🚀 Training time: {str(training_elapsed).split('.')[0]}")
                
                last_status = current_status
            
            # Check if completed
            if current_status in ['Completed', 'Failed', 'Stopped']:
                final_time = datetime.now() - start_time
                logger.info(f"\n🎯 Training job {current_status.upper()}!")
                logger.info(f"⏱️ Total monitoring time: {str(final_time).split('.')[0]}")
                
                if training_start:
                    training_time = datetime.now(timezone.utc) - training_start
                    logger.info(f"🚀 Actual training time: {str(training_time).split('.')[0]}")
                
                return response
            
            # Wait 2 minutes before next check
            time.sleep(120)
            
        except KeyboardInterrupt:
            logger.info("\n⚠️ Monitoring interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            time.sleep(30)
    
    return {}

def show_training_results(job_details: Dict[str, Any]):
    """Show detailed training results."""
    
    if not job_details:
        logger.warning("No job details available")
        return
    
    job_name = job_details['TrainingJobName']
    status = job_details['TrainingJobStatus']
    
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 TRAINING RESULTS: {job_name}")
    logger.info(f"{'='*60}")
    
    # Basic info
    logger.info(f"📊 Status: {status}")
    logger.info(f"🕐 Created: {job_details.get('CreationTime', 'N/A')}")
    
    if 'TrainingStartTime' in job_details:
        logger.info(f"🚀 Started: {job_details['TrainingStartTime']}")
    
    if 'TrainingEndTime' in job_details:
        logger.info(f"🏁 Ended: {job_details['TrainingEndTime']}")
        
        # Calculate training duration
        if 'TrainingStartTime' in job_details:
            start = job_details['TrainingStartTime']
            end = job_details['TrainingEndTime']
            duration = end - start
            logger.info(f"⏱️ Duration: {str(duration).split('.')[0]}")
    
    # Instance info
    resource_config = job_details.get('ResourceConfig', {})
    logger.info(f"💻 Instance: {resource_config.get('InstanceType', 'N/A')}")
    logger.info(f"🔢 Count: {resource_config.get('InstanceCount', 'N/A')}")
    
    # Model artifacts
    if 'ModelArtifacts' in job_details:
        artifacts = job_details['ModelArtifacts']
        logger.info(f"📦 Model Output: {artifacts.get('S3ModelArtifacts', 'N/A')}")
    
    # Failure reason if failed
    if status == 'Failed' and 'FailureReason' in job_details:
        logger.error(f"❌ Failure Reason: {job_details['FailureReason']}")
    
    # Final metrics if available
    if 'FinalMetricDataList' in job_details:
        metrics = job_details['FinalMetricDataList']
        if metrics:
            logger.info(f"\n📈 Final Metrics:")
            for metric in metrics:
                name = metric.get('MetricName', 'Unknown')
                value = metric.get('Value', 'N/A')
                logger.info(f"   • {name}: {value}")
    
    # Next steps
    logger.info(f"\n🎯 NEXT STEPS:")
    if status == 'Completed':
        logger.info("✅ Training completed successfully!")
        logger.info("🔄 Model is ready for testing and deployment")
        logger.info("📊 You can now test the model's accuracy")
        logger.info("🚀 Consider deploying to SageMaker endpoint for inference")
    elif status == 'Failed':
        logger.error("❌ Training failed - check logs for details")
        logger.info("🔍 Review hyperparameters and dataset")
        logger.info("🔄 Consider rerunning with adjusted settings")
    
    logger.info(f"{'='*60}")

def main():
    """Main monitoring function."""
    
    job_name = "paddleocr-thai-training-1754289824"
    
    logger.info("🚀 Starting Training Job Monitor")
    logger.info("🎯 Will wait until training completes and show results")
    logger.info("⚠️ Press Ctrl+C to stop monitoring (training will continue)")
    
    # Wait for completion
    job_details = wait_for_training_completion(job_name)
    
    # Show results
    if job_details:
        show_training_results(job_details)
    else:
        logger.warning("Could not retrieve final job details")

if __name__ == "__main__":
    main()
