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

## Repository Structure

```text
sagemaker_thai-ocr/                 # Project root
├── doc/                           # Documentation (Markdown files)
│   ├── overview.md               # This file - project overview
│   ├── scripts.md                # Scripts documentation and usage
│   ├── installation.md           # Setup and installation guide
│   ├── dataset.md                # Dataset preparation guide
│   ├── training.md               # Training procedures
│   ├── deployment.md             # Deployment instructions
│   └── terraform.md              # Infrastructure as Code
├── scripts/                       # Automation and management scripts
│   ├── aws_manager.py            # AWS resource management
│   ├── sagemaker_trainer.py      # SageMaker training jobs
│   └── deploy.sh                 # Complete deployment automation
├── thai-letters/                  # Data generation and conversion scripts
├── terraform/                     # Infrastructure as Code
│   ├── main.tf                   # Main Terraform configuration
│   ├── variables.tf              # Variable definitions
│   ├── resources.tf              # AWS resource definitions
│   └── outputs.tf                # Output definitions
├── test_aws_permissions.py        # AWS permissions validation
├── required_permissions.json      # Required AWS permissions
├── development-task.md            # Development task checklist
└── README.md                      # Project README
```

## Components

### 🔧 **Infrastructure & Automation**
- **AWS Management**: `scripts/` directory contains automation scripts for AWS resource management
- **Infrastructure as Code**: Terraform configurations for reproducible infrastructure
- **Permissions Management**: Validation and testing tools for AWS access

### 📊 **Data Management**
- **Data Generation**: Python and batch scripts in `thai-letters/` to create and annotate Thai OCR data
- **Data Conversion**: Scripts to convert annotations into PaddleOCR format
- **Synthetic Data**: Automated generation of Thai text images for training

### 🤖 **Machine Learning**
- **Training**: PaddleOCR training pipeline, local and SageMaker modes
- **Model Management**: Scripts for training job creation and monitoring
- **Inference**: Python tools for image recognition using trained models

### 📚 **Documentation & Development**
- **Comprehensive Documentation**: Detailed guides for all project aspects
- **Development Workflow**: Task tracking and development procedures
- **Script Documentation**: Complete reference for all automation scripts

## Script Integration

The project includes several key automation scripts that integrate with the overall workflow:

- **`scripts/aws_manager.py`**: Manages AWS resources (S3, ECR, IAM) following security policies
- **`scripts/sagemaker_trainer.py`**: Handles SageMaker training job lifecycle
- **`scripts/deploy.sh`**: End-to-end deployment automation
- **`test_aws_permissions.py`**: Validates AWS permissions and connectivity

For detailed information about scripts, see [`doc/scripts.md`](scripts.md).
