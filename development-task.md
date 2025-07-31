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

- [x] Copy and customize PaddleOCR config for Thai recognition ✅
  - **Generated 3 configs**: `thai_rec.yml`, `thai_rec_dev.yml`, `thai_rec_prod.yml`
  - **Source**: `thai_svtr_tiny_config.yml` from dataset
  - **Location**: `configs/rec/`
- [x] Update `character_dict_path` to use `th_dict.txt` ✅
  - **Path**: `thai-letters/datasets/converted/train_data_thai_paddleocr_0730_1648/train_data/th_dict.txt`
  - **Characters**: 880 Thai characters
- [x] Adjust hyperparameters (epochs, batch size, learning rate) ✅
  - **Dev config**: 10 epochs, batch 64, lr 0.001
  - **Main config**: 100 epochs, batch 128, lr 0.001
  - **Prod config**: 200 epochs, batch 256, lr 0.0005

## 4. Model Training

- [x] Local training ✅
  - **Script**: `python scripts/training/run_local_training.py --config dev --gpu false`
  - **Config**: `configs/rec/thai_rec_dev.yml` (10 epochs, batch 64, CPU training)
  - **Status**: Successfully started training process
  - **Dependencies**: PaddlePaddle 3.1.0 (CPU), PaddleOCR, all required packages
- [ ] SageMaker training (ด้วย Terraform)
  - **เตรียมข้อมูล**: Upload training data to S3 bucket (ใช้ AWS CLI หรือ boto3)
  - **สร้าง Docker image**: Build และ push PaddleOCR training image ไปยัง ECR
  - **กำหนดค่า Terraform**: เพิ่ม SageMaker Training Job resource
  - **รัน Terraform**: `terraform plan` และ `terraform apply` เพื่อสร้าง training job
  - **Monitor**: ติดตาม training job status ผ่าน AWS Console หรือ CLI

## 5. Infrastructure as Code (Terraform)

- [x] Define Terraform variables (`project_id`, `environment`, `aws_region`) ✅
- [x] Provision S3 bucket for data and models ✅
- [x] Provision ECR repository for Docker image ✅
- [x] Create IAM roles and policies for SageMaker ✅
- [ ] **เพิ่ม SageMaker Training Job resource** ใน `terraform/resources.tf`:
  - `aws_sagemaker_training_job` สำหรับ Thai OCR training
  - Training configuration (instance type, hyperparameters, S3 paths)
  - Output configuration สำหรับ model artifacts
- [ ] **เพิ่ม training variables** ใน `terraform/variables.tf`:
  - `training_instance_type` (default: `ml.m5.large`)
  - `training_epochs`, `training_batch_size`, `training_learning_rate`
  - `max_training_time` สำหรับ stopping condition
- [ ] **อัปเดต terraform.tfvars** ด้วยค่า training parameters
- [ ] **เตรียมข้อมูลการ training**:
  - Upload training data ไปยัง S3: `aws s3 sync thai-letters/datasets/converted/ s3://[bucket]/data/training/`
  - Build Docker image: `docker build -t thai-ocr-training .`
  - Push to ECR: `docker tag thai-ocr-training:latest [ecr-uri]:latest && docker push [ecr-uri]:latest`
- [ ] **รัน Terraform สำหรับ SageMaker Training**:
  ```bash
  cd terraform/
  terraform init
  terraform plan -target=aws_sagemaker_training_job.thai_ocr_training
  terraform apply -target=aws_sagemaker_training_job.thai_ocr_training
  ```
- [ ] **ติดตาม Training Job**:
  ```bash
  aws sagemaker describe-training-job --training-job-name [job-name]
  aws logs tail /aws/sagemaker/TrainingJobs --follow
  ```

## 6. Deployment & Inference (Terraform)

- [ ] **เพิ่ม SageMaker Model และ Endpoint resources** ใน Terraform:
  - `aws_sagemaker_model` สำหรับ trained model
  - `aws_sagemaker_endpoint_configuration` สำหรับ endpoint config
  - `aws_sagemaker_endpoint` สำหรับ real-time inference
- [ ] **กำหนดค่า inference variables**:
  - `inference_instance_type` (default: `ml.m5.large`)
  - `min_capacity`, `max_capacity` สำหรับ auto-scaling
- [ ] **Deploy ด้วย Terraform**:
  ```bash
  terraform plan -target=aws_sagemaker_endpoint.thai_ocr_endpoint
  terraform apply -target=aws_sagemaker_endpoint.thai_ocr_endpoint
  ```
- [ ] **Test endpoint** ใช้ AWS CLI หรือ boto3:
  ```bash
  aws sagemaker-runtime invoke-endpoint \
    --endpoint-name thai-ocr-endpoint \
    --body fileb://test_image.jpg \
    --content-type image/jpeg output.json
  ```

## 7. Documentation & Maintenance

- [ ] Keep `doc/` files up to date:
  - `overview.md`, `installation.md`, `dataset.md`, `training.md`, `deployment.md`, `terraform.md`
  - **`scripts.md`** - Document all automation scripts with usage examples
- [ ] Update top-level `README.md` and `development-task.md`
- [ ] Review and refine GitHub Copilot instructions (`.github/copilot-instructions.md`)
- [ ] **CRITICAL**: Update `doc/scripts.md` whenever creating or modifying scripts
- [ ] Plan next feature or improvements (e.g., more fonts, advanced augmentation)
