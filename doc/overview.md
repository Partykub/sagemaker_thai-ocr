# Project Overview

This document provides a high-level overview of the Thai OCR project, its goals, architecture, and primary components.

## Goals

- Develop a robust Optical Character Recognition (OCR) engine for the Thai language using PaddleOCR.
- Support custom training and fine-tuning for domain-specific documents.
- Deploy and manage training and inference workflows on AWS SageMaker.
- Automate infrastructure provisioning with Terraform.

## Architecture

```text
+-------------------+       +-------------------+       +------------------------+
|                   |       |                   |       |                        |
|  Thai Letter Data |  ---> |  Data Conversion  |  ---> |  PaddleOCR Training    |
|                   |       |  & Preprocessing  |       |  (Local / SageMaker)   |
+-------------------+       +-------------------+       +------------------------+
                                     |                              |
                                     v                              v
                          +----------------------+       +------------------------+
                          |  Synthetic Data      |       |  Trained Model Artifacts|
                          |  Generation Scripts  |       |  (S3 / Local)          |
                          +----------------------+       +------------------------+
                                                                     |
                                                                     v
                                                      +-------------------------+
                                                      |  Inference & Deployment |
                                                      |  (Local / SageMaker)    |
                                                      +-------------------------+
```

## Current Project Status

**Phase**: Data preparation completed, ready for Configuration & Training

### Completed ✅
- **Environment Setup**: Python virtual environment, AWS CLI, Terraform
- **Synthetic Data Generation**: 3,870 Thai OCR images (3,117 train, 753 val)
- **Dataset Format**: PaddleOCR-compatible format ready for training
- **Infrastructure Setup**: AWS CLI configured, Terraform initialized

### In Progress 🔄
- **Configuration**: Setting up PaddleOCR config files for Thai recognition
- **Model Training**: Preparing local and SageMaker training pipelines

### Upcoming 📋
- **Model Training**: Train PaddleOCR model with Thai dataset
- **Deployment**: Deploy trained model on SageMaker endpoint
- **Infrastructure**: Complete Terraform provisioning for production

## Repository Structure

```text
sagemaker_ocr_thai/                          # Project root
├── doc/                                    # Documentation (Markdown files)
├── scripts/                                # Setup and configuration scripts
│   ├── configure_aws_cli.ps1              # ✅ AWS CLI setup
│   ├── install_terraform.ps1              # ✅ Terraform installation
│   ├── setup_env.ps1                      # Python environment setup
│   └── install_deps.ps1                   # Dependencies installation
├── thai-letters/                           # Data generation scripts
│   ├── train_data_thai_phase1_0729_1331/  # ✅ Generated dataset (3,870 images)
│   │   └── train_data/rec/                # PaddleOCR format data
│   │       ├── rec_gt_train.txt           # Training labels (3,117)
│   │       ├── rec_gt_val.txt             # Validation labels (753)
│   │       └── thai_data/                 # Image files (train/, val/)
│   ├── quick_phase1_generator.py          # ✅ Main data generator
│   └── ...other generation scripts...     # Alternative generators
├── th_dict.txt                            # Thai character dictionary
└── development-task.md                    # ✅ Updated task tracking
```

## Components

- **Data Generation**: Python and batch scripts in `thai-letters/` to create and annotate Thai OCR data.
- **Data Conversion**: Scripts to convert annotations into PaddleOCR format.
- **Training**: PaddleOCR training pipeline, local and SageMaker modes.
- **Inference**: Python tools for image recognition using trained models.
- **Infrastructure**: Terraform modules and AWS Lambda functions to provision SageMaker resources.
