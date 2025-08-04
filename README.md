# Thai OCR Project

A comprehensive Optical Character Recognition (OCR) solution for the Thai language built on PaddleOCR. This project provides scripts for data generation, dataset conversion, model training, and deployment on AWS SageMaker with infrastructure managed by Terraform.

## Repository Layout

```text
sagemaker_thai-ocr/                # Project root
├── doc/                           # Full project documentation (English)
│   ├── README.md                  # Documentation index
│   ├── overview.md                # Project overview
│   ├── scripts.md                 # Scripts documentation
│   ├── installation.md            # Setup and installation
│   ├── dataset.md                 # Data generation & conversion  
│   ├── training.md                # Training pipeline
│   ├── deployment.md              # Deployment & inference
│   └── terraform.md               # Terraform IaC guide
├── scripts/                       # Automation and management scripts
│   ├── infrastructure/            # AWS resource management
│   │   ├── aws_manager.py         # AWS resource management
│   │   └── deploy.sh              # Complete deployment automation
│   ├── ml/                        # Machine learning operations
│   │   └── sagemaker_trainer.py   # SageMaker training jobs
│   ├── testing/                   # Testing and validation
│   │   └── test_aws_permissions.py # AWS permissions validation
│   ├── training/                  # Training configuration and execution
│   │   ├── setup_training_config.py # Training config setup
│   │   └── sagemaker_train.py     # SageMaker training entry point
│   ├── continue_deployment_v2.py  # Complete Docker build and deployment
│   └── utils/                     # Utility scripts
├── thai-letters/                  # Data generation and conversion scripts
├── terraform/                     # Infrastructure as Code
├── configs/                       # Training configuration files
│   └── rec/                       # Recognition model configs
├── requirements.txt               # Python dependencies with ML packages
├── Dockerfile.sagemaker          # Docker container for SageMaker training
├── test_aws_permissions.py       # AWS permissions validation
├── required_permissions.json     # Required AWS permissions
├── development-task.md           # Development task checklist
└── README.md (this file)         # Project overview and quick start
```  

## Quick Start

### 1. Environment Setup
```bash
# Test AWS permissions
python scripts/testing/test_aws_permissions.py

# Setup infrastructure
python scripts/infrastructure/aws_manager.py

# Or use complete deployment
./scripts/infrastructure/deploy.sh
```

### 2. Data Preparation
```bash
# Generate synthetic Thai data
python thai-letters/quick_phase1_generator.py --output synthetic_data/ --count 1000

# Convert to PaddleOCR format
python thai-letters/phase1_paddleocr_converter.py --input-path thai_dataset_... --output-path train_data_thai_paddleocr_...

# Setup training configurations
python scripts/training/setup_training_config.py
```

### 3. Training
```bash
# Local training (testing)
python PaddleOCR/tools/train.py -c configs/rec/thai_rec_dev.yml

# SageMaker training (production)
python scripts/continue_deployment_v2.py

# Monitor training progress
aws logs tail /aws/sagemaker/TrainingJobs --follow
```

### 4. Model Usage & Inference
```bash
# Quick single image inference
cd PaddleOCR
python tools/infer_rec.py \
  -c "../configs/rec/thai_rec_trained.yml" \
  -o Global.pretrained_model="../models/sagemaker_trained/best_model/model" \
  Global.infer_img="path/to/image.jpg"

# Batch processing multiple images
python scripts/ml/comprehensive_test.py

# Model testing and validation
python scripts/testing/direct_model_test.py
```

### 5. Scripts Reference
For detailed script usage, see [`doc/scripts.md`](doc/scripts.md):
- **Infrastructure**: `scripts/infrastructure/aws_manager.py`, `scripts/infrastructure/deploy.sh`
- **Training**: `scripts/continue_deployment_v2.py`, `scripts/training/sagemaker_train.py`
- **Configuration**: `scripts/training/setup_training_config.py`
- **Testing**: `scripts/testing/test_aws_permissions.py`
- **Model Usage**: See [`doc/model-usage.md`](doc/model-usage.md) for comprehensive inference guide

## Recent Updates

### Latest Features (August 2025)
- ✅ **Complete dependency resolution**: Fixed all Python and system library dependencies
- ✅ **Enhanced Docker support**: Improved Dockerfile.sagemaker with OpenGL libraries
- ✅ **SageMaker optimization**: CPU-only training configuration for SageMaker compatibility  
- ✅ **Automated deployment**: `continue_deployment_v2.py` for complete build and deploy pipeline
- ✅ **Training configuration**: Automated setup with `setup_training_config.py`
- ✅ **S3 path optimization**: Corrected data structure for efficient training data access

### Known Working Configuration
- **Python packages**: scikit-image, rapidfuzz, albumentations, imgaug, lmdb, scipy, matplotlib
- **System libraries**: libgl1-mesa-glx for OpenGL support
- **PaddleOCR settings**: CPU-only, distributed=False for SageMaker
- **S3 structure**: `/data/training/rec/` with proper label and image paths

## Documentation Links

- [Project Overview](doc/overview.md)
- [Scripts Documentation](doc/scripts.md) - **Complete guide to all automation scripts**
- [Installation & Setup](doc/installation.md)
- [Dataset Generation & Conversion](doc/dataset.md)
- [Training Pipeline](doc/training.md)
- [Deployment & Inference](doc/deployment.md)
- [Terraform Infrastructure](doc/terraform.md)
- [Development Task List](development-task.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
