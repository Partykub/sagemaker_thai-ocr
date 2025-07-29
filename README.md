# Thai OCR Project

A comprehensive Optical Character Recognition (OCR) solution for the Thai language built on PaddleOCR. This project provides scripts for data generation, dataset conversion, model training, and deployment on AWS SageMaker with infrastructure managed by Terraform.

## 🎯 Current Status

**Phase**: Data preparation completed ✅ - Ready for model training

- **✅ Completed**: Environment setup, AWS CLI configuration, Terraform setup, Synthetic dataset generation (3,870 images)
- **🔄 In Progress**: PaddleOCR configuration for Thai recognition
- **📋 Next**: Model training and deployment

## 📁 Repository Layout

```text
sagemaker_ocr_thai/                          # Project root
├── doc/                                    # Full project documentation
├── scripts/                                # Setup and configuration scripts
│   ├── configure_aws_cli.ps1              # ✅ AWS CLI setup
│   ├── install_terraform.ps1              # ✅ Terraform installation  
│   ├── setup_env.ps1                      # Python environment setup
│   └── install_deps.ps1                   # Dependencies installation
├── thai-letters/                           # Data generation scripts
│   ├── train_data_thai_phase1_0729_1331/  # ✅ Ready dataset (3,870 images)
│   │   └── train_data/rec/                # PaddleOCR format
│   │       ├── rec_gt_train.txt           # 3,117 training samples
│   │       ├── rec_gt_val.txt             # 753 validation samples
│   │       └── thai_data/                 # Image files
│   ├── quick_phase1_generator.py          # ✅ Main data generator
│   └── ...other scripts...                # Alternative generators
├── th_dict.txt                            # Thai character dictionary
├── development-task.md                    # ✅ Task tracking
└── README.md (this file)                  # Project overview
```  

## 🚀 Quick Start

### 1. Environment Setup
```powershell
# Configure AWS CLI
powershell -ExecutionPolicy Bypass -File .\scripts\configure_aws_cli.ps1 -Profile default

# Install Terraform and initialize
powershell -ExecutionPolicy Bypass -File .\scripts\install_terraform.ps1

# Set up Python environment
powershell -ExecutionPolicy Bypass -File .\scripts\setup_env.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\install_deps.ps1
```

### 2. Verify Dataset (Already Available)
```powershell
cd thai-letters\train_data_thai_phase1_0729_1331\train_data\rec

# Check training samples
Get-Content rec_gt_train.txt | Measure-Object -Line  # Should show 3117

# Check validation samples  
Get-Content rec_gt_val.txt | Measure-Object -Line    # Should show 753
```

### 3. Next Steps - Model Training
```bash
# Configure PaddleOCR for Thai (upcoming)
# Train locally or on SageMaker
# Deploy trained model
```

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
