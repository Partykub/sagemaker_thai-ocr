# Scripts Documentation

This document outlines all scripts in the Thai OCR project, their purposes, usage, and when to use them.

## Overview

The `scripts/` directory contains automation and management scripts for the Thai OCR project. Scripts are organized by functionality and follow consistent naming conventions.

## Script Categories

### 🔧 **Infrastructure Management**
Scripts for managing AWS resources and infrastructure deployment.

### 🤖 **Machine Learning**
Scripts for training, inference, and model management.

### 📊 **Testing & Validation**
Scripts for testing permissions, validating setups, and monitoring.

---

## Script Reference

### Infrastructure Management Scripts

#### `scripts/infrastructure/aws_manager.py`
**Purpose**: Comprehensive AWS resource management for Thai OCR project

**Description**: 
- Creates and manages S3 buckets, ECR repositories, and IAM roles
- Follows the `paddleocr-*` naming convention required by permissions
- Provides setup for complete project infrastructure

**Usage**:
```bash
# Run infrastructure setup
python scripts/infrastructure/aws_manager.py

# Or import as module
from scripts.infrastructure.aws_manager import ThaiOCRAWSManager
manager = ThaiOCRAWSManager()
resources = manager.setup_project_infrastructure("paddleocr-dev")
```

**When to use**:
- First-time project setup
- Creating new environments (dev, staging, prod)
- When you need to create AWS resources programmatically
- Before running SageMaker training jobs

**Key Features**:
- ✅ S3 bucket creation with versioning
- ✅ ECR repository setup with scanning
- ✅ IAM role creation for SageMaker
- ✅ Automatic permission validation
- ✅ Resource naming following security policies

---

#### `scripts/infrastructure/deploy.sh`
**Purpose**: Complete deployment automation script

**Description**:
- End-to-end deployment pipeline for Thai OCR project
- Interactive deployment with confirmation prompts
- Handles Docker image building and pushing to ECR
- Integrates with Terraform for infrastructure deployment

**Usage**:
```bash
# Make executable (first time only)
chmod +x scripts/infrastructure/deploy.sh

# Run deployment
./scripts/infrastructure/deploy.sh

# Or run specific components interactively
./scripts/infrastructure/deploy.sh  # Follow prompts for selective deployment
```

**When to use**:
- Complete project deployment
- Setting up new environments
- Deploying after major code changes
- When you need Docker image updates

**Interactive Options**:
- ✅ Infrastructure setup via Python scripts
- ✅ Optional Terraform deployment
- ✅ Docker image build and push
- ✅ Sample data structure creation

---

### Training Configuration Scripts

#### `scripts/training/setup_training_config.py`
**Purpose**: Setup and configure PaddleOCR training configurations for Thai OCR

**Description**: 
- Automatically discovers latest converted dataset
- Creates multiple training configurations (dev, main, prod)
- Updates dictionary paths and data directories
- Adjusts hyperparameters for different training scenarios

**Usage**:
```bash
# Run Task 3: Configuration setup
python scripts/training/setup_training_config.py

# Output: configs/rec/ directory with 3 config files
# - thai_rec_dev.yml: 10 epochs for quick testing
# - thai_rec.yml: 100 epochs for main training
# - thai_rec_prod.yml: 200 epochs for production
```

**When to use**:
- After completing data preparation (Task 2)
- Before starting local or SageMaker training (Task 4)
- When you need different training configurations
- Setting up new training environments

**Key Features**:
- ✅ Automatic dataset discovery and path configuration
- ✅ Character dictionary path updates (th_dict.txt)
- ✅ Multiple hyperparameter configurations
- ✅ Data validation and verification
- ✅ Comprehensive completion report generation

---

### Machine Learning Scripts

#### `scripts/ml/sagemaker_trainer.py`
**Purpose**: SageMaker training job management

**Description**:
- Creates and manages SageMaker training jobs
- Monitors training progress and logs
- Handles model creation and registration
- Designed to work with limited AWS permissions

**Usage**:
```bash
# Run training job
python scripts/ml/sagemaker_trainer.py

# Or use as module
from scripts.ml.sagemaker_trainer import ThaiOCRSageMakerTrainer
trainer = ThaiOCRSageMakerTrainer()

# Create training job
success = trainer.create_training_job(
    job_name="paddleocr-thai-training-20250730",
    role_arn="arn:aws:iam::484468818942:role/paddleocr-dev-sagemaker-role",
    image_uri="484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:latest",
    s3_input_path="s3://paddleocr-dev-data/training/",
    s3_output_path="s3://paddleocr-dev-data/models/"
)
```

**When to use**:
- Training Thai OCR models on SageMaker
- Monitoring existing training jobs
- Creating models for inference
- Scaling training beyond local resources

**Key Features**:
- ✅ Training job creation and monitoring
- ✅ Hyperparameter configuration
- ✅ Model artifact management
- ✅ CloudWatch integration for logging
- ✅ Training job status tracking

---

#### `scripts/training/sagemaker_train.py`
**Purpose**: SageMaker training container entry point

**Description**:
- Main training script that runs inside SageMaker training container
- Configures PaddleOCR for CPU-only training (SageMaker optimized)
- Handles S3 data paths and training configuration
- Integrates with Docker container environment

**Usage**:
```bash
# Inside SageMaker container (automated)
python /opt/ml/code/scripts/training/sagemaker_train.py \
    --train /opt/ml/input/data/training \
    --epochs 50

# Local testing (with proper paths)
python scripts/training/sagemaker_train.py \
    --train ./train_data_thai_paddleocr_v1 \
    --epochs 10
```

**When to use**:
- Automatically executed by SageMaker training jobs
- Testing training configuration locally
- Debugging training container issues
- Custom training parameter adjustment

**Key Features**:
- ✅ Automatic CPU/GPU configuration for SageMaker
- ✅ S3 data path handling and validation
- ✅ PaddleOCR configuration management
- ✅ Training and validation dataset setup
- ✅ Model output and artifact handling

---

#### `scripts/continue_deployment_v2.py`
**Purpose**: Comprehensive Docker build and SageMaker deployment automation

**Description**:
- Automated Docker image building with dependency resolution
- Handles ECR authentication and image pushing
- Creates and manages SageMaker training jobs
- Includes comprehensive error handling and status monitoring

**Usage**:
```bash
# Run complete deployment pipeline
python scripts/continue_deployment_v2.py

# The script automatically:
# 1. Builds Docker image with latest requirements
# 2. Pushes to ECR repository
# 3. Creates SageMaker training job
# 4. Monitors training progress
```

**When to use**:
- Complete deployment after code or dependency changes
- Automated CI/CD pipeline integration
- When Docker dependencies need updating
- Deploying new training configurations

**Key Features**:
- ✅ Automatic Docker image building and caching
- ✅ ECR authentication and image management
- ✅ SageMaker job creation with proper configuration
- ✅ Real-time training progress monitoring
- ✅ Comprehensive error handling and logging
- ✅ S3 data path validation and setup

---

### Testing & Validation Scripts

#### `scripts/testing/test_aws_permissions.py`
**Purpose**: AWS permissions validation and testing

**Description**:
- Validates all required AWS permissions are working
- Tests connectivity to S3, IAM, ECR, and SageMaker
- Generates detailed permission report
- Essential for troubleshooting access issues

**Usage**:
```bash
# Run permission tests
python scripts/testing/test_aws_permissions.py

# View results
cat aws_permissions_test_results.json
```

**When to use**:
- After initial AWS setup
- When experiencing permission errors
- Before starting training jobs
- During environment troubleshooting
- Regular health checks

**Output**:
- ✅ JSON report: `aws_permissions_test_results.json`
- ✅ Console logs with detailed status
- ✅ Service-by-service validation results
- ✅ Resource inventory (buckets, roles, repositories)

---

## Script Dependencies

### Required Python Packages
All scripts require these packages (installed via project setup):
```
boto3>=1.39.16
sagemaker>=2.248.2
scikit-image>=0.19.0
lmdb>=1.4.0
imgaug>=0.4.0
albumentations>=1.3.0
scipy>=1.9.0
matplotlib>=3.6.0
rapidfuzz>=2.0.0
```

### Docker Dependencies
Container requires these system packages:
```
libgl1-mesa-glx        # OpenGL support for OpenCV
libglib2.0-0           # GLib library
libsm6 libxext6        # X11 libraries
libxrender-dev         # X11 rendering
libgomp1              # OpenMP support
```

### AWS Configuration
Scripts require properly configured AWS credentials:
```bash
aws configure
# or use environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=ap-southeast-1
```

### Permission Requirements
Scripts are designed to work with the permissions defined in `required_permissions.json`:
- S3: `paddleocr-*` buckets
- IAM: `paddleocr-*` roles and policies  
- ECR: `paddleocr-*` repositories
- SageMaker: Full access for training and inference
- CloudWatch: Logging access

---

## Common Usage Patterns

### Initial Project Setup
```bash
# 1. Test permissions
python scripts/testing/test_aws_permissions.py

# 2. Setup infrastructure
python scripts/infrastructure/aws_manager.py

# 3. Full deployment (optional)
./scripts/infrastructure/deploy.sh
```

### Training Workflow
```bash
# 1. Prepare data (see thai-letters/ scripts)
python thai-letters/quick_phase1_generator.py
python thai-letters/phase1_paddleocr_converter.py

# 2. Setup training configurations
python scripts/training/setup_training_config.py

# 3. Test locally (optional)
python PaddleOCR/tools/train.py -c configs/rec/thai_rec_dev.yml

# 4. Deploy to SageMaker
python scripts/continue_deployment_v2.py

# 5. Monitor training progress
aws logs tail /aws/sagemaker/TrainingJobs --follow
```

### Docker Development Workflow
```bash
# 1. Update dependencies
# Edit requirements.txt with new packages

# 2. Test Docker build locally
docker build -f Dockerfile.sagemaker -t test-thai-ocr .

# 3. Clear cache if needed
docker system prune -af

# 4. Deploy with updated container
python scripts/continue_deployment_v2.py
```

### Troubleshooting
```bash
# Check permissions
python scripts/testing/test_aws_permissions.py

# Check AWS CLI config
aws configure list
aws sts get-caller-identity
```

---

## Error Handling

### Common Issues and Solutions

**Permission Denied Errors**:
- Run `python test_aws_permissions.py` to validate access
- Check that resource names follow `paddleocr-*` pattern
- Verify AWS credentials are current

**Training Job Failures**:
- Check CloudWatch logs via AWS Console
- Verify S3 paths and data format
- Ensure Docker image is properly built and pushed

**Docker Build Issues**:
- **ModuleNotFoundError for dependencies**: Update `requirements.txt` with missing packages
- **libGL.so.1 missing**: Add `libgl1-mesa-glx` to Dockerfile system packages
- **Container build failures**: Clear Docker cache with `docker system prune -af`
- **Dependency conflicts**: Check package versions in requirements.txt

**PaddleOCR Training Issues**:
- **Distributed training errors**: Disable GPU and distributed training for SageMaker
- **Data path errors**: Ensure S3 paths point to correct directory structure
- **rapidfuzz missing**: Add `rapidfuzz>=2.0.0` to requirements.txt
- **scikit-image missing**: Add `scikit-image>=0.19.0` to requirements.txt

**S3 Data Structure Issues**:
- **FileNotFoundError for labels**: Check that `rec_gt_train.txt` and `rec_gt_val.txt` exist
- **Image path errors**: Verify thai_data/train/ contains training images
- **Path configuration**: Update data_dir in training config to include '/rec/' suffix

**Resource Already Exists**:
- Scripts handle existing resources gracefully
- Use unique suffixes for resource names when needed

**ECR Authentication Issues**:
- Run `aws ecr get-login-password` to refresh Docker login
- Verify ECR repository exists and has proper permissions
- Check AWS region configuration matches ECR region

---

## Script Maintenance

### Adding New Scripts
When creating new scripts:

1. **Follow naming conventions**:
   - Use descriptive names: `feature_action.py` or `action_feature.sh`
   - Place in appropriate `scripts/` subdirectory if needed

2. **Update documentation**:
   - Add entry to this file (`doc/scripts.md`)
   - Include purpose, usage, and when to use
   - Update other relevant documentation

3. **Follow code standards**:
   - Include docstrings and comments
   - Add error handling and logging
   - Test with limited permissions

4. **Update related files**:
   - Add to `.gitignore` if generates temporary files
   - Update `README.md` if script is user-facing
   - Update `development-task.md` if part of workflow

### Script Organization

```
scripts/
├── infrastructure/             # AWS resource management
│   ├── aws_manager.py         # Main AWS resource manager
│   └── deploy.sh              # Complete deployment automation
├── ml/                        # Machine learning operations
│   └── sagemaker_trainer.py   # SageMaker training jobs
├── testing/                   # Testing and validation
│   └── test_aws_permissions.py # AWS permissions validation
└── utils/                     # Utility scripts (future)
    ├── data_helpers.py        # Data processing utilities
    └── monitoring.py          # Monitoring and alerting
```

---

## Integration with Other Components

### With Terraform
- Scripts complement Terraform for dynamic resource creation
- Use scripts for resources that need runtime configuration
- Terraform handles static infrastructure

### With thai-letters/
- Data preparation scripts in `thai-letters/` generate training data
- Scripts in `scripts/` handle cloud deployment and training
- Clear separation between data generation and cloud operations

### With Documentation
- All scripts must be documented in this file
- Usage examples should be practical and tested
- Keep documentation updated when scripts change

---

## Future Enhancements

### Planned Scripts
- `scripts/ml/inference_endpoint.py`: SageMaker endpoint management
- `scripts/ml/model_deployment.py`: Model versioning and deployment
- `scripts/utils/monitoring.py`: Training and inference monitoring
- `scripts/utils/data_pipeline.py`: Automated data preparation pipeline
- `scripts/infrastructure/cost_optimizer.py`: AWS cost optimization tools

### Improvement Areas
- Enhanced error handling and retry logic
- Configuration file support (YAML/JSON)
- Integration with CI/CD pipelines
- Automated testing for scripts
- Cross-platform compatibility enhancements