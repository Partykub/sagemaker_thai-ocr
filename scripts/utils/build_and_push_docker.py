#!/usr/bin/env python3
"""
Build and Push Docker Image to ECR for SageMaker Training
"""

import os
import boto3
import subprocess
import logging
import json
import base64
from pathlib import Path

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )
    return logging.getLogger(__name__)

def get_ecr_info():
    """Get ECR repository URL from Terraform outputs"""
    try:
        result = subprocess.run(
            ['terraform', 'output', '-json'],
            cwd='terraform',
            capture_output=True,
            text=True,
            check=True
        )
        
        outputs = json.loads(result.stdout)
        ecr_url = outputs['ecr_repository_url']['value']
        
        logger = logging.getLogger(__name__)
        logger.info(f"Found ECR repository: {ecr_url}")
        
        # Extract repository name and region
        # Format: 123456789012.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev
        parts = ecr_url.split('.')
        account_id = parts[0]
        region = parts[3]
        repo_name = ecr_url.split('/')[-1]
        
        return {
            'url': ecr_url,
            'account_id': account_id,
            'region': region,
            'repository_name': repo_name
        }
        
    except Exception as e:
        raise Exception(f"Failed to get ECR info from Terraform: {e}")

def ecr_login(region):
    """Login to ECR"""
    logger = logging.getLogger(__name__)
    
    try:
        # Get ECR login token
        ecr_client = boto3.client('ecr', region_name=region)
        token = ecr_client.get_authorization_token()
        
        username, password = token['authorizationData'][0]['authorizationToken'].encode('utf-8')
        username, password = base64.b64decode(username, password).decode('utf-8').split(':')
        registry = token['authorizationData'][0]['proxyEndpoint']
        
        # Docker login
        cmd = f'echo {password} | docker login --username {username} --password-stdin {registry}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ ECR login successful")
            return True
        else:
            logger.error(f"❌ ECR login failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ ECR login failed: {e}")
        return False

def build_docker_image(tag):
    """Build Docker image"""
    logger = logging.getLogger(__name__)
    
    try:
        cmd = [
            'docker', 'build',
            '-f', 'Dockerfile.sagemaker',
            '-t', tag,
            '.'
        ]
        
        logger.info(f"Building Docker image: {tag}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Docker build successful")
            return True
        else:
            logger.error(f"❌ Docker build failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Docker build failed: {e}")
        return False

def push_docker_image(local_tag, remote_tag):
    """Push Docker image to ECR"""
    logger = logging.getLogger(__name__)
    
    try:
        # Tag image for ECR
        tag_cmd = ['docker', 'tag', local_tag, remote_tag]
        result = subprocess.run(tag_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Docker tag failed: {result.stderr}")
            return False
        
        # Push image
        push_cmd = ['docker', 'push', remote_tag]
        logger.info(f"Pushing Docker image: {remote_tag}")
        result = subprocess.run(push_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Docker push successful")
            return True
        else:
            logger.error(f"❌ Docker push failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Docker push failed: {e}")
        return False

def main():
    """Main function to build and push Docker image"""
    logger = setup_logging()
    logger.info("Starting Docker build and push for SageMaker")
    
    try:
        # Get ECR info
        ecr_info = get_ecr_info()
        
        # Login to ECR
        if not ecr_login(ecr_info['region']):
            return False
        
        # Build Docker image
        local_tag = f"thai-ocr-sagemaker:latest"
        if not build_docker_image(local_tag):
            return False
        
        # Push Docker image
        remote_tag = f"{ecr_info['url']}:latest"
        if not push_docker_image(local_tag, remote_tag):
            return False
        
        logger.info(f"🎉 Docker image successfully pushed to ECR!")
        logger.info(f"📍 Image URI: {remote_tag}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Build and push failed: {e}")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
