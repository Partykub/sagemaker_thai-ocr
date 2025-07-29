# Amazon Q Rules for Thai OCR Project

## Project Context

This is a Thai OCR project using PaddleOCR with AWS SageMaker deployment and Terraform infrastructure management.

### Key Components
- **thai-letters/**: Data generation and annotation scripts
- **train_data_thai_paddleocr_.../**: PaddleOCR-ready datasets
- **configs/**: YAML configuration files for models
- **ppocr/utils/dict/**: Thai character dictionary
- **doc/**: Project documentation
- **scripts/**: Setup and utility scripts

## Code Generation Guidelines

### Path Conventions
- Use project-root-relative paths for consistency
- Reference data paths from project root
- Maintain absolute paths for AWS resources

### Script Organization
- Keep data generation, conversion, training, and inference modular
- Separate AWS-specific code into dedicated modules
- Use clear function names with docstrings

### AWS Integration
- Follow AWS SDK best practices
- Include proper error handling for AWS calls
- Use consistent resource tagging
- Implement retry logic for API calls

### Terraform Standards
- Group resources by function (S3, ECR, IAM, Lambda)
- Use clear, descriptive resource names
- Include proper variable definitions
- Add output values for resource references

### Documentation Alignment
- Keep code consistent with doc/ markdown files
- Update doc/scripts.md when adding new scripts
- Reference correct file paths in documentation

## Common Development Tasks

1. **Data Generation**: Create/update generators in thai-letters/
2. **Model Configuration**: Modify configs under configs/rec/
3. **Training Scripts**: Implement SageMaker training and Lambda handlers
4. **Infrastructure**: Add Terraform resources for AWS components
5. **Documentation**: Update relevant doc/ files

## Coding Standards

- Use Python type hints where applicable
- Include comprehensive logging
- Implement proper exception handling
- Follow PEP 8 style guidelines
- Add unit tests for critical functions