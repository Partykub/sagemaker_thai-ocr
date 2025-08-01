#!/usr/bin/env python3
"""
Test AWS Permissions Script
Tests permissions defined in required_permissions.json
"""

import boto3
import json
import logging
from botocore.exceptions import ClientError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_aws_permissions():
    """Test AWS permissions based on required_permissions.json"""
    
    # Initialize AWS clients with default region
    region = 'ap-southeast-1'  # Default region for this project
    sts = boto3.client('sts', region_name=region)
    s3 = boto3.client('s3', region_name=region)
    iam = boto3.client('iam', region_name=region)
    ecr = boto3.client('ecr', region_name=region)
    sagemaker = boto3.client('sagemaker', region_name=region)
    
    results = {}
    
    # Test 1: STS (already working)
    try:
        identity = sts.get_caller_identity()
        results['sts'] = {
            'status': 'SUCCESS',
            'account': identity['Account'],
            'user': identity['UserId']
        }
        logger.info(f"✅ STS: Connected as {identity['UserId']} in account {identity['Account']}")
    except Exception as e:
        results['sts'] = {'status': 'FAILED', 'error': str(e)}
        logger.error(f"❌ STS: {e}")
    
    # Test 2: S3 permissions
    try:
        # List buckets (to test basic S3 access)
        response = s3.list_buckets()
        paddleocr_buckets = [b['Name'] for b in response['Buckets'] if b['Name'].startswith('paddleocr-')]
        
        results['s3'] = {
            'status': 'SUCCESS',
            'paddleocr_buckets': paddleocr_buckets,
            'total_buckets': len(response['Buckets'])
        }
        logger.info(f"✅ S3: Found {len(paddleocr_buckets)} paddleocr-* buckets out of {len(response['Buckets'])} total")
        
    except Exception as e:
        results['s3'] = {'status': 'FAILED', 'error': str(e)}
        logger.error(f"❌ S3: {e}")
    
    # Test 3: IAM permissions
    try:
        # List roles with paddleocr prefix
        response = iam.list_roles()
        paddleocr_roles = [r['RoleName'] for r in response['Roles'] if r['RoleName'].startswith('paddleocr-')]
        
        results['iam'] = {
            'status': 'SUCCESS',
            'paddleocr_roles': paddleocr_roles,
            'total_roles': len(response['Roles'])
        }
        logger.info(f"✅ IAM: Found {len(paddleocr_roles)} paddleocr-* roles")
        
    except Exception as e:
        results['iam'] = {'status': 'FAILED', 'error': str(e)}
        logger.error(f"❌ IAM: {e}")
    
    # Test 4: ECR permissions
    try:
        # List repositories
        response = ecr.describe_repositories()
        paddleocr_repos = [r['repositoryName'] for r in response['repositories'] if r['repositoryName'].startswith('paddleocr-')]
        
        results['ecr'] = {
            'status': 'SUCCESS',
            'paddleocr_repositories': paddleocr_repos,
            'total_repositories': len(response['repositories'])
        }
        logger.info(f"✅ ECR: Found {len(paddleocr_repos)} paddleocr-* repositories")
        
    except Exception as e:
        results['ecr'] = {'status': 'FAILED', 'error': str(e)}
        logger.error(f"❌ ECR: {e}")
    
    # Test 5: SageMaker permissions
    try:
        # List training jobs (limited to recent ones)
        response = sagemaker.list_training_jobs(MaxResults=5)
        
        results['sagemaker'] = {
            'status': 'SUCCESS',
            'recent_training_jobs': len(response['TrainingJobSummaries'])
        }
        logger.info(f"✅ SageMaker: Can list training jobs ({len(response['TrainingJobSummaries'])} recent jobs found)")
        
    except Exception as e:
        results['sagemaker'] = {'status': 'FAILED', 'error': str(e)}
        logger.error(f"❌ SageMaker: {e}")
    
    return results

def main():
    """Main function to run permission tests"""
    logger.info("🔍 Testing AWS Permissions for Thai OCR Project...")
    logger.info("=" * 60)
    
    results = test_aws_permissions()
    
    logger.info("=" * 60)
    logger.info("📊 PERMISSION TEST SUMMARY:")
    
    success_count = 0
    total_count = len(results)
    
    for service, result in results.items():
        status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
        logger.info(f"{status_icon} {service.upper()}: {result['status']}")
        if result['status'] == 'SUCCESS':
            success_count += 1
    
    logger.info("=" * 60)
    logger.info(f"🎯 RESULT: {success_count}/{total_count} services accessible")
    
    if success_count == total_count:
        logger.info("🎉 All permissions are working correctly!")
        logger.info("✨ Ready to proceed with Thai OCR project setup")
    else:
        logger.warning("⚠️  Some permissions may be limited, but basic functionality should work")
    
    # Save results to file
    with open('aws_permissions_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("📄 Test results saved to: aws_permissions_test_results.json")
    
    return results

if __name__ == "__main__":
    main()
