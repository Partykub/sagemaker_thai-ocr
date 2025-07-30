# GitHub Copilot Instructions for Thai OCR Project

This file provides comprehensive context and guidance for GitHub Copilot to assist with code suggestions and completions across the Thai OCR project.

## Project Overview

- **Objective**: Build a robust OCR engine for Thai language using PaddleOCR, with support for custom training, AWS SageMaker deployment, and Terraform-managed infrastructure.
- **Main Components**:
  - **thai-letters/**: Python and batch scripts for synthetic and real Thai text image generation and annotation
  - **train_data_thai_paddleocr_.../**: Converted dataset ready for PaddleOCR training (image/, label/, train_list.txt, val_list.txt)
  - **configs/**: YAML configuration files for detection and recognition models (e.g., `thai_svtr_tiny_config.yml`)
  - **ppocr/utils/dict/**: Thai character dictionary (`th_dict.txt`)
  - **doc/**: Comprehensive documentation in Markdown format
  - **terraform/**: Infrastructure as Code for AWS resources
  - **scripts/**: Utility and deployment scripts
  - **.github/copilot-instructions.md**: This instruction file

## Directory Structure Rules

```text
sagemaker_thai-ocr/                # Project root
├── .amazonq/                      # Amazon Q configuration
│   └── rules/                     # Amazon Q rules directory
├── .github/                       # GitHub configuration
│   └── copilot-instructions.md    # GitHub Copilot instructions
├── doc/                           # Full project documentation (English)
│   ├── README.md                  # Documentation index
│   ├── overview.md                # Project overview
│   ├── installation.md            # Setup and installation
│   ├── dataset.md                 # Data generation & conversion
│   ├── training.md                # Training pipeline
│   ├── deployment.md              # Deployment & inference
│   └── terraform.md               # Terraform IaC guide
├── thai-letters/                  # Data generation and conversion scripts
├── train_data_thai_paddleocr_*/   # Converted PaddleOCR datasets
├── configs/                       # YAML configuration files
│   └── rec/                       # Recognition model configs
├── ppocr/utils/dict/              # Character dictionaries
├── scripts/                       # Utility and deployment scripts
├── terraform/                     # Infrastructure as Code
├── th_dict.txt                    # Comprehensive Thai character dictionary
└── README.md                      # Project overview and quick start
```

## Path and Naming Conventions

### Absolute Paths
- Always use project-root-relative paths when referencing files
- Example: `thai-letters/quick_phase1_generator.py` not `./thai-letters/quick_phase1_generator.py`

### File Naming Standards
- **Python Files**: Use snake_case, prefix with purpose (`train_`, `generate_`, `convert_`, `deploy_`)
- **Configuration Files**: Descriptive names with purpose (`thai_rec_config.yml`, `thai_det_config.yml`)
- **Data Files**: Include version or date (`train_data_thai_paddleocr_v1/`, `synthetic_data_20240130/`)
- **Documentation**: Use lowercase with hyphens (`installation.md`, `dataset-generation.md`)

## Usage Context

### Data Generation and Processing
- Generate synthetic Thai text images with various fonts and styles
- Create real Thai text annotations and labels
- Convert datasets to PaddleOCR format with proper structure
- Handle large-scale data processing efficiently

### Model Training
- **Local Training**: Using `PaddleOCR/tools/train.py` with custom configurations
- **SageMaker Training**: Via AWS Lambda or Step Functions, containerized in Docker, pushed to ECR
- **Distributed Training**: Multi-GPU and multi-node training on SageMaker
- Implement hyperparameter tuning strategies

### Inference & Deployment
- **Local Inference**: Using Python scripts and PaddleOCR API
- **Real-time Inference**: Via SageMaker endpoints for live OCR processing
- **Batch Inference**: For processing large volumes of documents
- Configure auto-scaling and monitoring

### Infrastructure as Code
- Terraform scripts for S3 buckets, ECR repositories, IAM roles
- Lambda functions for training orchestration
- SageMaker resources for training and inference
- Implement proper security and access controls

## Python Code Standards

### Type Hints and Error Handling
```python
# Always include proper imports and type hints
import logging
from typing import Dict, List, Optional, Tuple
import boto3
from pathlib import Path

def process_thai_text(
    text: str, 
    config: Dict[str, Any],
    output_path: Optional[Path] = None
) -> Tuple[bool, str]:
    """Process Thai text with proper error handling."""
    try:
        # Implementation here
        logging.info(f"Processing text: {text[:50]}...")
        return True, "Success"
    except Exception as e:
        logging.error(f"Error processing text: {e}")
        return False, str(e)
```

### AWS SDK Best Practices
```python
# Use boto3 sessions with proper error handling
import boto3
from botocore.exceptions import ClientError

def upload_to_s3(file_path: str, bucket: str, key: str) -> bool:
    """Upload file to S3 with proper error handling."""
    try:
        s3_client = boto3.client('s3')
        s3_client.upload_file(file_path, bucket, key)
        logging.info(f"Successfully uploaded {file_path} to s3://{bucket}/{key}")
        return True
    except ClientError as e:
        logging.error(f"Failed to upload to S3: {e}")
        return False
```

## Thai Language Specific Rules

### Character Set Management
```python
# Thai character dictionary management
THAI_CHARACTERS = {
    'consonants': [
        'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ', 
        'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ', 
        'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ษ', 
        'ส', 'ห', 'ฬ', 'อ', 'ฮ'
    ],
    'vowels': [
        'ะ', 'ั', 'า', 'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'เ', 'แ', 'โ', 
        'ใ', 'ไ', 'ๅ', 'ๆ', '็', '่', '้', '๊', '๋', '์'
    ],
    'numbers': ['๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙'],
    'punctuation': ['ฯ', '๏', '๚', '๛'],
    'special': [' ', '\n', '\t']
}
```

### Text Processing Rules
- Always use UTF-8 encoding for Thai text processing
- Handle Thai character complexity (vowels, tone marks, consonants)
- Consider Thai text rendering and font requirements
- Implement proper Thai text validation
- Account for Thai character stacking and positioning

## PaddleOCR Configuration Standards

### Recognition Model Configuration Template
```yaml
Global:
  use_gpu: true
  epoch_num: 100
  log_smooth_window: 20
  print_batch_step: 10
  save_model_dir: ./output/thai_rec/
  save_epoch_step: 10
  eval_batch_step: 500
  cal_metric_during_train: true
  character_dict_path: ppocr/utils/dict/th_dict.txt
  character_type: th
  max_text_length: 25
  infer_mode: false
  use_space_char: true
  distributed: true

Architecture:
  model_type: rec
  algorithm: SVTR_LCNet
  Backbone:
    name: SVTRNet
    img_size: [64, 256]
    out_char_num: 25
    out_channels: 192

Loss:
  name: CTCLoss

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: 0.001
    warmup_epoch: 5
```

## AWS Infrastructure Best Practices

### Resource Naming Convention
```hcl
# Consistent naming across all resources
locals {
  name_prefix = "thai-ocr-${var.environment}"
  
  common_tags = {
    Project     = "thai-ocr"
    Environment = var.environment
    ManagedBy   = "terraform"
    Owner       = var.owner
    CostCenter  = var.cost_center
  }
}
```

### Security and IAM
- Use IAM least privilege principle
- Implement proper VPC configuration for secure training
- Configure CloudWatch monitoring and logging
- Use Spot instances for cost optimization

## Docker and Deployment Standards

### Multi-stage Dockerfile Pattern
```dockerfile
FROM python:3.8-slim as base
# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ml/code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Training stage
FROM base as training
COPY scripts/ scripts/
COPY configs/ configs/
ENV PYTHONPATH=/opt/ml/code
ENTRYPOINT ["python", "scripts/training/train.py"]

# Inference stage  
FROM base as inference
COPY scripts/inference/ scripts/inference/
COPY models/ models/
EXPOSE 8080
ENTRYPOINT ["python", "scripts/inference/serve.py"]
```

## Testing and Quality Standards

### Testing Framework Requirements
- Unit tests for all Thai text processing functions
- Integration tests for PaddleOCR conversion
- AWS service integration tests with mocking
- Performance benchmarks for model inference
- Load testing for inference endpoints
- Data quality validation tests

### Code Quality Rules
- Minimum 80% test coverage
- Use pre-commit hooks for code formatting
- Black for Python code formatting
- Flake8 for linting with max line length 88
- Type hints required for all functions

### Model Quality Metrics
```python
def calculate_ocr_metrics(predictions: List[str], ground_truth: List[str]) -> Dict[str, float]:
    """Calculate OCR-specific quality metrics."""
    return {
        'character_accuracy': char_accuracy,
        'word_accuracy': word_accuracy, 
        'average_edit_distance': avg_edit_distance,
        'normalized_edit_distance': normalized_distance
    }
```

## Error Handling Standards

### Standard Error Handling Pattern
```python
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def safe_operation(data: Any) -> Optional[Any]:
    """Template for safe operations with proper error handling."""
    try:
        result = process_data(data)
        logger.info("Operation completed successfully")
        return result
    except ValueError as e:
        logger.error(f"Invalid data provided: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

### AWS Error Handling with Retry Logic
```python
from botocore.exceptions import ClientError, NoCredentialsError
import time

def aws_operation_with_retry(operation_func, max_retries: int = 3):
    """AWS operation with retry logic."""
    for attempt in range(max_retries):
        try:
            return operation_func()
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['Throttling', 'ServiceUnavailable'] and attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            logger.error(f"AWS operation failed: {e}")
            raise
```

## Copilot Code Generation Guidelines

1. **Consistent Paths**: Use absolute or project-root-relative paths for data, configs, and model artifacts
2. **Modular Design**: Keep data generation, conversion, training, and inference in separate modules
3. **AWS Best Practices**: Follow AWS SDK best practices with proper error handling and retry logic
4. **Thai Language Support**: Always consider Thai character complexity and UTF-8 encoding
5. **Configuration Management**: Centralize configuration loading with environment-specific overrides
6. **Security First**: Implement proper IAM policies, VPC configurations, and encryption
7. **Performance Optimization**: Use appropriate instance types, spot instances, and caching strategies
8. **Monitoring**: Include comprehensive logging, metrics, and alerting
9. **Testing**: Write comprehensive tests for all components with proper mocking
10. **Documentation**: Maintain consistency with existing documentation structure

## Common Development Tasks

### Data Pipeline Tasks
- Create or update data generators in `thai-letters/`
- Implement PaddleOCR dataset conversion with validation
- Optimize data processing for large-scale operations
- Handle Thai font rendering and image generation

### Model Training Tasks
- Update PaddleOCR configurations under `configs/rec/`
- Implement distributed training on SageMaker
- Set up hyperparameter tuning experiments
- Monitor training progress and implement early stopping

### Deployment Tasks
- Create SageMaker training and inference scripts
- Implement Lambda orchestration functions
- Set up real-time and batch inference endpoints
- Configure CI/CD pipelines with GitHub Actions

### Infrastructure Tasks
- Design Terraform modules for AWS components
- Implement security and compliance requirements
- Set up monitoring and cost optimization
- Configure auto-scaling and disaster recovery

---

_End of comprehensive Copilot instructions._
