#!/usr/bin/env python3
"""
AWS Resources Management Script for Thai OCR
Uses permissions defined in required_permissions.json
"""

import boto3
import json
import logging
import os
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ThaiOCRAWSManager:
    def __init__(self, region_name: str = "ap-southeast-1"):
        """Initialize AWS manager with limited permissions."""
        self.region = region_name
        self.s3 = boto3.client('s3', region_name=region_name)
        self.ecr = boto3.client('ecr', region_name=region_name)
        self.iam = boto3.client('iam', region_name=region_name)
        
    def create_s3_bucket(self, bucket_name: str) -> bool:
        """Create S3 bucket with paddleocr-* naming convention."""
        try:
            if not bucket_name.startswith('paddleocr-'):
                logger.warning(f"Bucket name {bucket_name} doesn't follow paddleocr-* pattern")
                return False
            
            # Create bucket
            if self.region == 'us-east-1':
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            
            # Enable versioning
            self.s3.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            logger.info(f"S3 bucket created successfully: {bucket_name}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                logger.info(f"Bucket {bucket_name} already exists and is owned by you")
                return True
            else:
                logger.error(f"Failed to create S3 bucket: {e}")
                return False
    
    def upload_to_s3(self, bucket_name: str, local_path: str, s3_key: str) -> bool:
        """Upload file to S3 bucket."""
        try:
            self.s3.upload_file(local_path, bucket_name, s3_key)
            logger.info(f"Successfully uploaded {local_path} to s3://{bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            return False
    
    def list_s3_objects(self, bucket_name: str, prefix: str = "") -> Optional[List[str]]:
        """List objects in S3 bucket."""
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            logger.error(f"Failed to list S3 objects: {e}")
            return None
    
    def create_ecr_repository(self, repo_name: str) -> Optional[str]:
        """Create ECR repository with paddleocr-* naming convention."""
        try:
            if not repo_name.startswith('paddleocr-'):
                logger.warning(f"Repository name {repo_name} doesn't follow paddleocr-* pattern")
                return None
            
            response = self.ecr.create_repository(
                repositoryName=repo_name,
                imageScanningConfiguration={'scanOnPush': True},
                imageTagMutability='MUTABLE'
            )
            
            repo_uri = response['repository']['repositoryUri']
            logger.info(f"ECR repository created successfully: {repo_uri}")
            return repo_uri
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'RepositoryAlreadyExistsException':
                # Get existing repository URI
                try:
                    response = self.ecr.describe_repositories(repositoryNames=[repo_name])
                    repo_uri = response['repositories'][0]['repositoryUri']
                    logger.info(f"ECR repository already exists: {repo_uri}")
                    return repo_uri
                except:
                    logger.error(f"Failed to get existing repository info: {e}")
                    return None
            else:
                logger.error(f"Failed to create ECR repository: {e}")
                return None
    
    def get_ecr_login_token(self) -> Optional[str]:
        """Get ECR authorization token for docker login."""
        try:
            response = self.ecr.get_authorization_token()
            token = response['authorizationData'][0]['authorizationToken']
            endpoint = response['authorizationData'][0]['proxyEndpoint']
            
            import base64
            username, password = base64.b64decode(token).decode().split(':')
            
            logger.info(f"ECR login token retrieved for {endpoint}")
            return f"docker login -u {username} -p {password} {endpoint}"
            
        except Exception as e:
            logger.error(f"Failed to get ECR login token: {e}")
            return None
    
    def create_iam_role(self, role_name: str, assume_role_policy: Dict[str, Any]) -> Optional[str]:
        """Create IAM role with paddleocr-* naming convention."""
        try:
            if not role_name.startswith('paddleocr-'):
                logger.warning(f"Role name {role_name} doesn't follow paddleocr-* pattern")
                return None
            
            response = self.iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description=f"IAM role for Thai OCR project - {role_name}"
            )
            
            role_arn = response['Role']['Arn']
            logger.info(f"IAM role created successfully: {role_arn}")
            return role_arn
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExistsException':
                # Get existing role ARN
                try:
                    response = self.iam.get_role(RoleName=role_name)
                    role_arn = response['Role']['Arn']
                    logger.info(f"IAM role already exists: {role_arn}")
                    return role_arn
                except:
                    logger.error(f"Failed to get existing role info: {e}")
                    return None
            else:
                logger.error(f"Failed to create IAM role: {e}")
                return None
    
    def attach_role_policy(self, role_name: str, policy_arn: str) -> bool:
        """Attach policy to IAM role."""
        try:
            self.iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
            logger.info(f"Policy {policy_arn} attached to role {role_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to attach policy to role: {e}")
            return False
    
    def setup_project_infrastructure(self, project_name: str = "paddleocr-dev") -> Dict[str, str]:
        """Setup basic infrastructure for Thai OCR project."""
        resources = {}
        
        # Create S3 bucket
        bucket_name = f"{project_name}-data-bucket"
        if self.create_s3_bucket(bucket_name):
            resources['s3_bucket'] = bucket_name
        
        # Create ECR repository
        repo_name = project_name
        repo_uri = self.create_ecr_repository(repo_name)
        if repo_uri:
            resources['ecr_repository'] = repo_uri
        
        # Create SageMaker execution role
        sagemaker_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "sagemaker.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        role_name = f"{project_name}-sagemaker-role"
        role_arn = self.create_iam_role(role_name, sagemaker_role_policy)
        if role_arn:
            resources['sagemaker_role_arn'] = role_arn
            
            # Attach basic SageMaker policies (if available)
            # Note: This might fail if user doesn't have permission to attach AWS managed policies
            try:
                self.attach_role_policy(role_name, "arn:aws:iam::aws:policy/AmazonSageMakerReadOnly")
            except:
                logger.warning("Could not attach AmazonSageMakerReadOnly policy - continuing without it")
        
        return resources

def main():
    """Main function to setup infrastructure."""
    manager = ThaiOCRAWSManager()
    
    # Setup project infrastructure
    resources = manager.setup_project_infrastructure("paddleocr-dev")
    
    logger.info("=== Infrastructure Setup Complete ===")
    for resource_type, resource_value in resources.items():
        logger.info(f"{resource_type}: {resource_value}")
    
    # Get ECR login command
    login_cmd = manager.get_ecr_login_token()
    if login_cmd:
        logger.info(f"ECR Login Command: {login_cmd}")
    
    return resources

if __name__ == "__main__":
    main()
