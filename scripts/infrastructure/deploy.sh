#!/bin/bash
# Thai OCR Deployment Script
# Uses permissions defined in required_permissions.json

set -e

# Configuration
PROJECT_NAME="paddleocr-dev"
AWS_REGION="ap-southeast-1"
AWS_ACCOUNT_ID="484468818942"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is configured
check_aws_cli() {
    echo_info "Checking AWS CLI configuration..."
    if ! aws sts get-caller-identity &>/dev/null; then
        echo_error "AWS CLI is not configured or credentials are invalid"
        echo "Please run: aws configure"
        exit 1
    fi
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo_info "Using AWS Account: $ACCOUNT_ID"
}

# Setup infrastructure using Python script
setup_infrastructure() {
    echo_info "Setting up AWS infrastructure..."
    
    if [ -f "scripts/aws_manager.py" ]; then
        python3 scripts/aws_manager.py
    else
        echo_error "aws_manager.py not found. Please ensure the script exists."
        exit 1
    fi
}

# Deploy with Terraform (optional)
deploy_terraform() {
    echo_info "Deploying infrastructure with Terraform..."
    
    if [ ! -d "terraform" ]; then
        echo_error "Terraform directory not found"
        exit 1
    fi
    
    cd terraform
    
    # Copy example tfvars if needed
    if [ ! -f "terraform.tfvars" ] && [ -f "terraform.tfvars.example" ]; then
        cp terraform.tfvars.example terraform.tfvars
        echo_warning "Created terraform.tfvars from example. Please review and update as needed."
    fi
    
    # Initialize and plan
    terraform init
    terraform plan
    
    # Ask for confirmation
    read -p "Do you want to apply these changes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply
        echo_info "Terraform deployment completed"
    else
        echo_info "Terraform deployment skipped"
    fi
    
    cd ..
}

# Build and push Docker image to ECR
build_and_push_docker() {
    echo_info "Building and pushing Docker image..."
    
    # Get ECR login token
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Repository name following the permission pattern
    REPO_NAME="$PROJECT_NAME"
    IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:latest"
    
    # Create Dockerfile if it doesn't exist
    if [ ! -f "Dockerfile" ]; then
        echo_info "Creating basic Dockerfile for PaddleOCR..."
        cat > Dockerfile << EOF
FROM python:3.8-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \\
    libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /opt/ml/code

# Copy requirements and install Python dependencies
COPY thai-letters/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install paddlepaddle paddleocr boto3 sagemaker

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/opt/ml/code
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

# Default command
CMD ["python", "scripts/sagemaker_trainer.py"]
EOF
    fi
    
    # Build image
    docker build -t $REPO_NAME .
    docker tag $REPO_NAME:latest $IMAGE_URI
    
    # Push to ECR
    docker push $IMAGE_URI
    
    echo_info "Docker image pushed to: $IMAGE_URI"
}

# Create sample training data structure
create_sample_data() {
    echo_info "Creating sample data structure..."
    
    mkdir -p sample_data/{images,labels}
    
    # Create sample train_list.txt
    cat > sample_data/train_list.txt << EOF
images/sample1.jpg	labels/sample1.txt
images/sample2.jpg	labels/sample2.txt
EOF
    
    # Create sample val_list.txt
    cat > sample_data/val_list.txt << EOF
images/val1.jpg	labels/val1.txt
EOF
    
    echo_info "Sample data structure created in sample_data/"
}

# Main deployment function
main() {
    echo_info "Starting Thai OCR deployment with limited permissions..."
    
    # Check prerequisites
    check_aws_cli
    
    # Setup infrastructure
    setup_infrastructure
    
    # Optional: Deploy with Terraform
    read -p "Do you want to deploy infrastructure with Terraform? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        deploy_terraform
    fi
    
    # Build and push Docker image
    read -p "Do you want to build and push Docker image? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_and_push_docker
    fi
    
    # Create sample data structure
    create_sample_data
    
    echo_info "Deployment completed successfully!"
    echo_info "Next steps:"
    echo "  1. Generate Thai OCR training data using thai-letters/ scripts"
    echo "  2. Upload training data to S3 bucket"
    echo "  3. Run SageMaker training job using scripts/sagemaker_trainer.py"
    echo "  4. Create inference endpoint for deployment"
}

# Run main function
main "$@"
