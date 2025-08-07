# Thai OCR Project

A comprehensive Optical Character Recognition (OCR) solution for the Thai language built on PaddleOCR. This project provides scripts for data generation, dataset conversion, model training, and deployment on AWS SageMaker with infrastructure managed by Terraform.

## 🎯 Project Status (August 6, 2025)

### ✅ Latest Updates - Enhanced Dataset Generator
- **Enhanced UI**: Interactive dictionary and effects selection
- **Improved Image Quality**: Increased image height from 64 to 96 pixels (+50%)
- **Flexible Effects**: Choose from 8 different OCR challenge types
- **Better Integration**: Seamless parameter passing between scripts
- **File Consolidation**: Single enhanced `thai_dataset_quick.py` file

### ✅ Completed Milestones
- **Data Generation**: Enhanced with interactive selection and flexible effects
- **Dataset Conversion**: Successfully converted to PaddleOCR format with train/validation split
- **Infrastructure Setup**: AWS SageMaker, ECR, S3 resources deployed via Terraform
- **Model Training**: 25+ hour training on SageMaker ml.g4dn.xlarge instance completed
- **Model Testing**: Single character inference working with 93.3% success rate
- **Configuration Verification**: Exact training/inference configuration match confirmed
- **Documentation**: Comprehensive guides and standardized testing procedures

### ⚠️ Current Challenge: Model Accuracy
- **Issue**: Model loads and executes successfully but predictions don't match ground truth
- **Status**: Model produces single characters (✅) but accuracy very low (~0%)
- **Investigation**: Focusing on training data quality and preprocessing consistency
- **Next Steps**: Data quality analysis and model performance optimization

### 📊 Current Metrics
- **Model Loading**: 100% success rate ✅
- **Inference Execution**: 93.3% success rate (14/15 samples) ✅  
- **Single Character Output**: Working correctly ✅
- **Character Accuracy**: Very low, needs improvement ⚠️
- **Configuration Consistency**: Verified exact match ✅

### 🔧 Current Training Configuration (VERIFIED WORKING)

#### **Model Architecture**
- **Algorithm**: CRNN + MobileNetV3
- **Backbone**: MobileNetV3 (scale: 0.5, model_name: large)
- **Neck**: SequenceEncoder (encoder_type: rnn, hidden_size: 96)
- **Head**: CTCHead (fc_decay: 0.00001)

#### **Model Files**
- **Primary Model**: `models/sagemaker_trained/best_accuracy.pdparams` (9,205,880 bytes)
- **Optimizer**: `models/sagemaker_trained/best_accuracy.pdopt`
- **Config**: `models/sagemaker_trained/config.yml` (2,262 bytes)
- **Alternative**: `models/sagemaker_trained/best_model/model.pdparams`

#### **Dictionary Configuration**
- **File**: `thai-letters/th_dict.txt` (7,323 bytes, 880 characters)
- **Character Types**: Thai characters, English letters, numbers, symbols
- **Encoding**: UTF-8

#### **Training Parameters**
- **Max Text Length**: 1 (Single Character Mode)
- **Character Type**: thai
- **Use Space Char**: false
- **Architecture**: CRNN + MobileNetV3 (same as inference)

## 🚀 Quick Start - Enhanced Dataset Generation

### Basic Usage
```bash
# Navigate to data generation folder
cd thai-letters

# Generate dataset with interactive selection
python thai_dataset_quick.py 10

# Follow the prompts:
# 1. Select dictionary file (number_dict.txt or th_dict.txt)
# 2. Choose effects (0=none, 9=all, or specific combinations like 1,2,3)
```

### Advanced Examples
```bash
# Quick test with no effects
python thai_dataset_quick.py 1
# → Choose dictionary → Select 0 (no effects) → Get clean images

# Standard training dataset
python thai_dataset_quick.py 20
# → Choose dictionary → Select 9 (all effects) → Get varied dataset

# Custom effects (rotation + brightness + blur)
python thai_dataset_quick.py 15
# → Choose dictionary → Select 1,2,4 → Get specific effects
```

### New Features ✨
- **Interactive Dictionary Selection**: Choose from available `*_dict.txt` files
- **Flexible Effects**: 8 OCR challenge types (rotation, brightness, contrast, blur, etc.)
- **Enhanced Image Size**: 128x96 pixels (+50% height for Thai characters)
- **Smart Naming**: Output folders include effects info automatically

### 🧪 Testing Configuration (STANDARDIZED)

#### **Primary Test Dataset**
- **Location**: `thai-letters/datasets/converted/train_data_thai_paddleocr_0804_1144/train_data/rec/rec_gt_val.txt`
- **Format**: `image_path\tground_truth_text`
- **Sample Count**: 15 validation samples
- **Examples**: 
  - `117_44.jpg → 'อุ้'`
  - `032_34.jpg → 'ค์'`
  - `121_15.jpg → 'ขั้'`

#### **Test Script**
- **Primary Script**: `test_sagemaker_model.py`
- **Config Used**: Auto-generated with exact training parameters
- **Success Rate**: 93.3% (14/15 samples working)
- **Output**: Single character results as designed

### ⚠️ Current Model Performance
- **Model Loading**: ✅ SUCCESS (100%)
- **Inference Execution**: ✅ SUCCESS (93.3%)
- **Single Character Output**: ✅ WORKING
- **Accuracy**: ❌ LOW (needs improvement - model predicts different characters)

Example Results:
- Ground Truth: `อุ้` → Predicted: `ซ`
- Ground Truth: `ค` → Predicted: `ช`
- Ground Truth: `จิ` → Predicted: `ก`

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

### 4. Model Testing & Inference (STANDARDIZED)

#### **Standard Testing Procedure**
```bash
# Use the verified configuration and test dataset
python test_sagemaker_model.py
```

#### **Manual Single Image Testing**
```bash
# Navigate to PaddleOCR directory
cd PaddleOCR

# Test with exact training configuration
python tools/infer_rec.py \
  -c "../test_inference_config.yml" \
  -o Global.infer_img="../test_images/thai_word_01_สวัสดี.jpg"
```

#### **Verified Configuration Parameters**
- **Model Path**: `../models/sagemaker_trained/best_accuracy`
- **Dictionary**: `../thai-letters/th_dict.txt` (880 characters)
- **Max Text Length**: 1 (single character mode)
- **Architecture**: CRNN + MobileNetV3 (exact match with training)
- **Character Type**: thai
- **Use Space Char**: false

#### **Test Dataset**
- **Primary**: `thai-letters/datasets/converted/train_data_thai_paddleocr_0804_1144/train_data/rec/rec_gt_val.txt`
- **Format**: Tab-separated (image_path\tground_truth)
- **Usage**: Standardized test set with known ground truth labels

### 5. Scripts Reference
For detailed script usage, see [`doc/scripts.md`](doc/scripts.md):
- **Infrastructure**: `scripts/infrastructure/aws_manager.py`, `scripts/infrastructure/deploy.sh`
- **Training**: `scripts/continue_deployment_v2.py`, `scripts/training/sagemaker_train.py`
- **Configuration**: `scripts/training/setup_training_config.py`
- **Testing**: `scripts/testing/test_aws_permissions.py`
- **Model Usage**: See [`doc/model-usage.md`](doc/model-usage.md) for comprehensive inference guide

## Recent Updates

### Training Completed (August 5, 2025)
- ✅ **SageMaker Training Completed**: 25+ hour training session completed successfully on `ml.g4dn.xlarge`
- ✅ **Model Artifacts Generated**: 6.5MB model files downloaded from S3 (`model.tar.gz`)
- ✅ **Model Files Available**: `model.pdparams`, `model.pdopt`, `best_accuracy.pdparams`, `config.yml`
- ⚠️ **Version Compatibility Issue**: Trained model incompatible with current PaddleOCR environment

### Current Status
- **Training Phase**: ✅ COMPLETED
- **Model Deployment**: ❌ BLOCKED by version mismatch
- **Issue**: PaddleOCR framework version mismatch between SageMaker training environment and local inference environment
- **Model Location**: `models/sagemaker_trained/` (6,516,294 bytes)

### Known Working Configuration (Training)
- ✅ **Python packages**: scikit-image, rapidfuzz, albumentations, imgaug, lmdb, scipy, matplotlib
- ✅ **System libraries**: libgl1-mesa-glx for OpenGL support
- ✅ **PaddleOCR settings**: CPU-only, distributed=False for SageMaker
- ✅ **S3 structure**: `/data/training/rec/` with proper label and image paths
- ✅ **Training completed**: 1 day, 1 hour, 17 minutes on AWS SageMaker

### Inference Issues
- ❌ **PaddleOCR API changes**: `TextRecognizer` import failures
- ❌ **Model format mismatch**: `.pdparams` files not compatible with current PaddleOCR version
- ❌ **Configuration incompatibility**: `set_optimization_level` attribute errors
- ⚠️ **Next Steps Required**: Environment alignment or model conversion needed

## Documentation Links

- [Project Overview](doc/overview.md)
- [Scripts Documentation](doc/scripts.md) - **Complete guide to all automation scripts**
- [Installation & Setup](doc/installation.md)
- [Dataset Generation & Conversion](doc/dataset.md)
- [Training Pipeline](doc/training.md)
- [Deployment & Inference](doc/deployment.md)
- [Terraform Infrastructure](doc/terraform.md)
- [Development Task List](development-task.md)

### 🇹🇭 เอกสารภาษาไทย (Thai Documentation)
- **[คู่มือการเทรน SageMaker](doc/sagemaker-training-guide.md)** - ครบวงจรการเทรน Thai OCR บน AWS SageMaker
- **[สรุปโครงการ](doc/thai-project-summary.md)** - ภาพรวมโครงการและแผนการพัฒนา

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
