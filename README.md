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
│   ├── infrastructure/          # AWS resource management
│   │   ├── aws_manager.py      # AWS resource management
│   │   └── deploy.sh           # Complete deployment automation
│   ├── ml/                     # Machine learning operations
│   │   └── sagemaker_trainer.py # SageMaker training jobs
│   ├── testing/                # Testing and validation
│   │   └── test_aws_permissions.py # AWS permissions validation
│   └── utils/                  # Utility scripts
├── thai-letters/                  # Data generation and conversion scripts
├── terraform/                     # Infrastructure as Code
├── scripts/testing/test_aws_permissions.py # AWS permissions validation
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
```

### 3. Training
```bash
# Local training
python PaddleOCR/tools/train.py -c configs/rec/thai_rec.yml

# SageMaker training
python scripts/ml/sagemaker_trainer.py
```

### 4. Scripts Reference
For detailed script usage, see [`doc/scripts.md`](doc/scripts.md):
- **Infrastructure**: `scripts/infrastructure/aws_manager.py`, `scripts/infrastructure/deploy.sh`
- **Training**: `scripts/ml/sagemaker_trainer.py` 
- **Testing**: `scripts/testing/test_aws_permissions.py`

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
