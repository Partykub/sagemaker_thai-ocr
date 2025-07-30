# Development Task List

This file outlines the key development tasks for the Thai OCR project, based on the documentation in `doc/`.

## 1. Environment & Setup

- [x] Create and activate Python virtual environment
- [x] Install project dependencies
  - `pip install -r thai-letters/requirements.txt`
  - `pip install paddlepaddle paddleocr boto3 sagemaker`
- [x] Configure AWS CLI credentials and permissions
- [x] Install Terraform and initialize project

## 2. Data Preparation

- [x] Generate synthetic Thai OCR data ✅
  - `thai-letters/quick_phase1_generator.py` - COMPLETED
  - `thai-letters/thai_dataset_generator.py` - COMPLETED
  - **Generated**: 8,768 images (879 Thai chars × 10 samples)
  - **Success rate**: 99.75% (8,768/8,790)
  - **Location**: `datasets/raw/thai_dataset_standard_10samples_0730_1646/`
- [ ] Annotate or collect real Thai document images
- [x] Convert annotations to PaddleOCR format ✅
  - `thai-letters/phase1_paddleocr_converter.py` - COMPLETED
  - **Converted**: 8,768 images → PaddleOCR format
  - **Train/Val split**: 7,014 train / 1,754 val (80/20)
  - **Location**: `datasets/converted/train_data_thai_paddleocr_0730_1648/`
- [x] Verify generated dataset structure: ✅
  - `train_data/rec/thai_data/train/` - 7,014 images
  - `train_data/rec/thai_data/val/` - 1,754 images  
  - `train_data/rec/rec_gt_train.txt` - training labels
  - `train_data/rec/rec_gt_val.txt` - validation labels
  - `th_dict.txt` - 880 Thai characters
  - `th_corpus.txt` - 9,672 Thai words
  - `thai_svtr_tiny_config.yml` - PaddleOCR config

## 3. Configuration

- [ ] Copy and customize PaddleOCR config for Thai recognition
  - `configs/rec/thai_rec.yml` or `thai_svtr_tiny_config.yml`
- [ ] Update `character_dict_path` to use `th_dict.txt`
- [ ] Adjust hyperparameters (epochs, batch size, learning rate)

## 4. Model Training

- [ ] Local training
  - `python PaddleOCR/tools/train.py -c configs/rec/thai_rec.yml`
- [ ] SageMaker training
  - Upload data to S3 (`s3://<bucket>/data/training/`)
  - Build and push Docker image to ECR
  - Configure and run training job via Lambda or Step Functions
  - Monitor job status and logs

## 5. Infrastructure as Code

- [ ] Define Terraform variables (`project_id`, `environment`, `aws_region`)
- [ ] Provision S3 bucket for data and models
- [ ] Provision ECR repository for Docker image
- [ ] Create IAM roles and policies for SageMaker and Lambda
- [ ] Deploy Lambda function to start SageMaker training
- [ ] Apply Terraform configuration (`terraform init`, `plan`, `apply`)

## 6. Deployment & Inference

- [ ] Build and register SageMaker model
- [ ] Create endpoint configuration and deploy endpoint
- [ ] Implement inference script for real-time prediction
- [ ] Test endpoint using SDK or CLI

## 7. Documentation & Maintenance

- [ ] Keep `doc/` files up to date:
  - `overview.md`, `installation.md`, `dataset.md`, `training.md`, `deployment.md`, `terraform.md`
  - **`scripts.md`** - Document all automation scripts with usage examples
- [ ] Update top-level `README.md` and `development-task.md`
- [ ] Review and refine GitHub Copilot instructions (`.github/copilot-instructions.md`)
- [ ] **CRITICAL**: Update `doc/scripts.md` whenever creating or modifying scripts
- [ ] Plan next feature or improvements (e.g., more fonts, advanced augmentation)
