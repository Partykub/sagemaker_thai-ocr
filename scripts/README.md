# Scripts Directory

This directory contains automation and management scripts for the Thai OCR project, organized by functionality.

## Directory Structure

```
scripts/
├── __init__.py                    # Package initialization
├── infrastructure/               # AWS resource management
│   ├── __init__.py
│   ├── aws_manager.py            # AWS resource management
│   └── deploy.sh                 # Complete deployment automation
├── ml/                           # Machine learning operations
│   ├── __init__.py
│   └── sagemaker_trainer.py      # SageMaker training jobs
├── testing/                      # Testing and validation
│   ├── __init__.py
│   └── test_aws_permissions.py   # AWS permissions validation
└── utils/                        # Utility scripts (future)
    └── __init__.py
```

## Quick Start

### Infrastructure Setup
```bash
# Test AWS permissions
python scripts/testing/test_aws_permissions.py

# Setup AWS resources
python scripts/infrastructure/aws_manager.py

# Complete deployment
./scripts/infrastructure/deploy.sh
```

### Machine Learning
```bash
# Run SageMaker training
python scripts/ml/sagemaker_trainer.py
```

## Import as Modules

Scripts can also be imported as Python modules:

```python
# Infrastructure management
from scripts.infrastructure.aws_manager import ThaiOCRAWSManager

# ML training
from scripts.ml.sagemaker_trainer import ThaiOCRSageMakerTrainer

# Testing
from scripts.testing.test_aws_permissions import test_aws_permissions
```

## Documentation

For detailed documentation of all scripts, see [`doc/scripts.md`](../doc/scripts.md).

## Requirements

- Python 3.8+
- boto3
- sagemaker
- Properly configured AWS credentials
- Permissions as defined in `required_permissions.json`

## Contributing

When adding new scripts:

1. Place in appropriate subdirectory
2. Update `doc/scripts.md` with usage documentation
3. Add import statements to relevant `__init__.py` files
4. Follow existing coding standards and error handling patterns
