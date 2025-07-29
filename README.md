# Thai OCR Project

A comprehensive Optical Character Recognition (OCR) solution for the Thai language built on PaddleOCR. This project provides scripts for data generation, dataset conversion, model training, and deployment on AWS SageMaker with infrastructure managed by Terraform.

## Repository Layout

```text
sagemaker_ocr_thai/                # Project root
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
├── th_dict.txt                    # Comprehensive Thai character dictionary
└── README.md (this file)          # Project overview and quick start
```  

## Quick Start

1. Read detailed documentation in the `doc/` folder:
   ```bash
   less doc/README.md
   ```

2. Install prerequisites and dependencies:
   ```bash
   # Create Python virtual environment
   python -m venv venv
   . venv/Scripts/Activate.ps1

   # Install packages
   pip install -r thai-letters/requirements.txt
   pip install paddlepaddle paddleocr boto3 sagemaker terraform
   ```

3. Generate or prepare your dataset:
   ```bash
   python thai-letters/quick_phase1_generator.py --output synthetic_data/ --count 1000 --fonts path/to/fonts
   python thai-letters/phase1_paddleocr_converter.py --input-path thai_dataset_... --output-path train_data_thai_paddleocr_...
   ```

4. Train locally:
   ```bash
   python PaddleOCR/tools/train.py -c configs/rec/thai_rec.yml -o Global.epoch_num=50
   ```

5. Deploy on AWS SageMaker:
   - Build and push Docker image to ECR
   - Provision AWS resources via Terraform
   - Trigger training with Lambda or SageMaker SDK

## Documentation Links

- [Project Overview](doc/overview.md)
- [Installation & Setup](doc/installation.md)
- [Dataset Generation & Conversion](doc/dataset.md)
- [Training Pipeline](doc/training.md)
- [Deployment & Inference](doc/deployment.md)
 - [Terraform Infrastructure](doc/terraform.md)
 - [Project Structure & File Organization](doc/structure.md)
 - [Script Reference](doc/scripts.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
