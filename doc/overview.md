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
sagemaker_ocr_thai/                  # Project root
├── doc/                            # Documentation (Markdown files)
├── thai-letters/                   # Data generation and conversion scripts
├── train_data_thai_paddleocr_.../  # Converted PaddleOCR dataset
├── th_dict.txt                     # Thai character dictionary
├── ...other project files...       # Training scripts, configs, notebooks
```

## Components

- **Data Generation**: Python and batch scripts in `thai-letters/` to create and annotate Thai OCR data.
- **Data Conversion**: Scripts to convert annotations into PaddleOCR format.
- **Training**: PaddleOCR training pipeline, local and SageMaker modes.
- **Inference**: Python tools for image recognition using trained models.
- **Infrastructure**: Terraform modules and AWS Lambda functions to provision SageMaker resources.
