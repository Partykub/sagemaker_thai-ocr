# 🚀 Thai OCR Manual Training Guide - วิธีเทรนจริงที่ใช้งานได้

## 📚 คู่มือการเทรนแบบ Manual บน AWS SageMaker

> **Updated**: 7 สิงหาคม 2025 - จากประสบการณ์การเทรนจริงที่สำเร็จ 100% ✅

### 🎯 **ผลลัพธ์จริงที่ได้**
- **Dataset**: Numbers 0-9 (304 ไฟล์)
- **Instance**: ml.g4dn.xlarge (GPU)
- **เวลาเทรน**: 13 นาทีเท่านั้น!
- **ค่าใช้จ่าย**: $0.11 USD
- **โมเดล**: CRNN + MobileNetV3 พร้อมใช้งาน

---

## 📋 สารบัญ

1. [การเตรียมระบบ](#1-การเตรียมระบบ)
2. [การอัปโหลดข้อมูล](#2-การอัปโหลดข้อมูล)
3. [การสร้าง Docker Image](#3-การสร้าง-docker-image)
4. [การตั้งค่า Training Configuration](#4-การตั้งค่า-training-configuration)
5. [การรัน Training Job](#5-การรัน-training-job)
6. [การดาวน์โหลดโมเดล](#6-การดาวน์โหลดโมเดล)
7. [การทดสอบโมเดล](#7-การทดสอบโมเดล)
8. [Tips & Best Practices](#8-tips--best-practices)

---

## 1. การเตรียมระบบ

### 1.1 AWS Credentials
```powershell
# ตั้งค่า AWS credentials (แนะนำใช้ temporary credentials)
$Env:AWS_ACCESS_KEY_ID="your_access_key"
$Env:AWS_SECRET_ACCESS_KEY="your_secret_key"
$Env:AWS_SESSION_TOKEN="your_session_token"

# ตรวจสอบ credentials
aws sts get-caller-identity
```

### 1.2 ตรวจสอบความพร้อม
```powershell
# รันสคริปต์ตรวจสอบระบบ
python scripts\training\validate_training_setup.py
```

**ผลลัพธ์ที่ต้องเป็น ✅**:
- AWS Credentials: ✅
- S3 Training Data: ✅  
- SageMaker IAM Role: ✅
- Local Configuration: ✅

---

## 2. การอัปโหลดข้อมูล

### 2.1 เตรียม Dataset
ข้อมูลต้องอยู่ในรูปแบบ PaddleOCR format:
```
train_data_thai_paddleocr_*/
├── rec_gt_train.txt    # Training labels
├── rec_gt_val.txt      # Validation labels  
└── thai_data/
    ├── train/          # Training images
    └── val/            # Validation images
```

### 2.2 อัปโหลดไป S3
```powershell
# อัปโหลดข้อมูลไป S3 (ใช้ sync เพื่อความเร็ว)
aws s3 sync "thai-letters\datasets\converted\train_data_thai_paddleocr_*" s3://paddleocr-dev-data-bucket/data/training/rec/ --exclude="*.log"

# ตรวจสอบการอัปโหลด
aws s3 ls s3://paddleocr-dev-data-bucket/data/training/rec/ --human-readable --recursive
```

**ตัวอย่างผลลัพธ์**:
```
2025-08-07 00:00:00    7.0 KiB data/training/rec/rec_gt_train.txt
2025-08-07 00:00:00    1.6 KiB data/training/rec/rec_gt_val.txt
2025-08-07 00:00:00  304 objects total (0.9 MiB)
```

---

## 3. การสร้าง Docker Image

### 3.1 Docker Build
```powershell
# Build Docker image สำหรับ SageMaker
docker build -f Dockerfile.sagemaker -t thai-numbers-ocr:latest .
```

### 3.2 Tag และ Push ไป ECR
```powershell
# ECR Login
aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin 484468818942.dkr.ecr.ap-southeast-1.amazonaws.com

# Tag image
docker tag thai-numbers-ocr:latest 484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:numbers-latest

# Push to ECR
docker push 484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:numbers-latest
```

**ผลลัพธ์ที่ได้**:
```
numbers-latest: digest: sha256:dcf985c0ac7cf990b946664ae77eb6b89239949a87b500bb4e2d35d3d0b300d5
```

---

## 4. การตั้งค่า Training Configuration

### 4.1 สร้างไฟล์ config สำหรับ Numbers
`configs/rec/numbers_config.yml`:
```yaml
Global:
  use_gpu: true
  epoch_num: 50                    # ลดลงเพราะ dataset เล็ก
  log_smooth_window: 20
  print_batch_step: 10
  save_model_dir: /opt/ml/model/
  save_epoch_step: 5
  eval_batch_step: 100
  cal_metric_during_train: true
  character_dict_path: /opt/ml/input/data/training/th_dict.txt
  character_type: thai
  max_text_length: 25
  infer_mode: false
  use_space_char: false
  save_inference_dir: /opt/ml/model/inference/

Architecture:
  model_type: rec
  algorithm: CRNN
  Transform:
  Backbone:
    name: MobileNetV3
    scale: 0.5
    model_name: large
  Neck:
    name: SequenceEncoder
    encoder_type: rnn
    hidden_size: 96
  Head:
    name: CTCHead
    fc_decay: 1e-05

Loss:
  name: CTCLoss

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: 0.005          # เพิ่มขึ้นเล็กน้อย
    warmup_epoch: 5

PostProcess:
  name: CTCLabelDecode

Metric:
  name: RecMetric
  main_indicator: acc

Train:
  dataset:
    name: SimpleDataSet
    data_dir: /opt/ml/input/data/training/rec/thai_data/
    label_file_list: ["/opt/ml/input/data/training/rec/rec_gt_train.txt"]
    transforms:
      - DecodeImage:
          img_mode: BGR
          channel_first: false
      - CTCLabelEncode:
      - RecResizeImg:
          image_shape: [3, 32, 128]   # ขนาดที่เหมาะสม
      - KeepKeys:
          keep_keys: ['image', 'label', 'length']
  loader:
    shuffle: true
    batch_size_per_card: 32        # เพิ่ม batch size
    drop_last: true
    num_workers: 4

Eval:
  dataset:
    name: SimpleDataSet
    data_dir: /opt/ml/input/data/training/rec/thai_data/
    label_file_list: ["/opt/ml/input/data/training/rec/rec_gt_val.txt"]
    transforms:
      - DecodeImage:
          img_mode: BGR
          channel_first: false
      - CTCLabelEncode:
      - RecResizeImg:
          image_shape: [3, 32, 128]
      - KeepKeys:
          keep_keys: ['image', 'label', 'length']
  loader:
    shuffle: false
    drop_last: false
    batch_size_per_card: 16
    num_workers: 2
```

### 4.2 สำคัญ! การเลือก Instance Type

| Instance Type | ราคา/ชั่วโมง | GPU | เหมาะสำหรับ | ใช้เวลา | ค่าใช้จ่ายจริง |
|---------------|-------------|-----|------------|--------|-------------|
| ml.m5.large   | $0.115     | ❌  | CPU only   | 3-4 ชม | $0.35-$0.46 |
| **ml.g4dn.xlarge** | **$0.526** | **✅** | **Small dataset** | **13 นาที** | **$0.11** ⭐ |
| ml.g4dn.2xlarge | $0.752    | ✅  | Large dataset | 8-10 นาที | $0.10-$0.12 |

**คำแนะนำ**: ใช้ **ml.g4dn.xlarge** - เร็วที่สุดและถูกที่สุดสำหรับ dataset เล็ก!

---

## 5. การรัน Training Job

### 5.1 รันสคริปต์ Training
```powershell
# รันการเทรนแบบ manual
python scripts\training\manual_numbers_training.py
```

### 5.2 ข้อมูลที่จะเห็น
```
🚀 Thai Numbers OCR - SageMaker Training
==================================================
📍 Region: ap-southeast-1
🐳 ECR Image: 484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:numbers-latest
📊 Input Data: s3://paddleocr-dev-data-bucket/data/training/
📦 Output Path: s3://paddleocr-dev-data-bucket/models/
🔧 Instance Type: ml.g4dn.xlarge (GPU)
==================================================
✅ Training job created successfully!
📊 Training Job ARN: arn:aws:sagemaker:ap-southeast-1:484468818942:training-job/thai-numbers-ocr-20250807-100059
```

---

## 6. การติดตามการเทรน

### 6.1 Real-time Monitoring
สคริปต์จะแสดงสถานะแบบ real-time:
```
[10:01:32] Status: InProgress | Secondary: Starting | Time: 0s
[10:03:32] Status: InProgress | Secondary: Downloading | Time: 30s  
[10:04:02] Status: InProgress | Secondary: Training | Time: 60s
[10:05:02] Status: InProgress | Secondary: Training | Time: 120s
...
[10:16:07] Status: Completed | Secondary: Completed | Time: 781s
```

### 6.2 ผลลัพธ์สุดท้าย
```
🏁 Training finished!
📊 Final Status: Completed
⏱️ Total Training Time: 781 seconds (~13 minutes)
💰 Billable Time: 781 seconds  
💵 Estimated Cost: $0.11 USD
📦 Model Artifacts: s3://paddleocr-dev-data-bucket/models/thai-numbers-ocr-20250807-100059/output/model.tar.gz
```

---

## 7. การดาวน์โหลดโมเดล

### 7.1 ดาวน์โหลดโมเดลที่เทรนแล้ว
```powershell
# รันสคริปต์ดาวน์โหลด
python scripts\training\download_trained_model.py
```

### 7.2 โครงสร้างโมเดลที่ได้
```
models/sagemaker_trained/
├── best_accuracy.pdparams       # Best model weights
├── config.yml                   # Training configuration
├── latest.pdparams              # Latest checkpoint
├── iter_epoch_*.pdparams        # Epoch checkpoints (every 5 epochs)
└── best_model/
    ├── inference.pdmodel        # ⭐ Ready-to-use model
    ├── inference.pdiparams      # Model parameters
    └── config.yml               # Model config
```

**สำคัญ**: ไฟล์ `best_model/inference.pdmodel` คือโมเดลที่พร้อมใช้งาน!

---

## 8. การทดสอบโมเดล

### 8.1 ทดสอบโมเดลขั้นพื้นฐาน
```powershell
# รันการทดสอบง่าย
python scripts\training\simple_model_test.py
```

### 8.2 ใช้งานโมเดลจริง
```python
from paddleocr import PaddleOCR

# Initialize with custom model
ocr = PaddleOCR(
    det_model_dir='models/sagemaker_trained/best_model/',
    rec_model_dir='models/sagemaker_trained/best_model/',
    use_angle_cls=True,
    lang='th'
)

# Test with image
result = ocr.ocr('path/to/number_image.jpg')
print(result)
```

---

## 9. Tips & Best Practices

### 9.1 การเลือก Instance Type
```
✅ DO: ใช้ ml.g4dn.xlarge สำหรับ dataset เล็ก (ถูก + เร็ว)
✅ DO: ใช้ ml.g4dn.2xlarge สำหรับ dataset ใหญ่
❌ DON'T: ใช้ CPU instance (ml.m5.*) สำหรับ deep learning
```

### 9.2 การปรับ Configuration
```yaml
# สำหรับ dataset เล็ก (< 1000 images)
epoch_num: 50
batch_size_per_card: 32
learning_rate: 0.005

# สำหรับ dataset ใหญ่ (> 10000 images)  
epoch_num: 100
batch_size_per_card: 64
learning_rate: 0.001
```

### 9.3 การประหยัดค่าใช้จ่าย
- ใช้ **Spot instances** ถ้าไม่เร่งด่วน (ประหยัด 50-70%)
- เลือก **instance type** ให้เหมาะกับขนาด dataset
- **Monitor** การเทรนแบบ real-time เพื่อหยุดเมื่อ converge

### 9.4 การแก้ไขปัญหาที่พบบ่อย

**1. AWS Credentials หมดอายุ**
```powershell
# ตั้งค่าใหม่
$Env:AWS_ACCESS_KEY_ID="new_key"
$Env:AWS_SECRET_ACCESS_KEY="new_secret"  
$Env:AWS_SESSION_TOKEN="new_token"
```

**2. Docker build ล้มเหลว**
```powershell
# ลบ cache และ build ใหม่
docker system prune -f
docker build --no-cache -f Dockerfile.sagemaker -t thai-numbers-ocr:latest .
```

**3. S3 permission error**
```powershell
# ตรวจสอบ bucket policy และ IAM permissions
aws s3 ls s3://paddleocr-dev-data-bucket/ --region ap-southeast-1
```

**4. Training job Failed**
- ตรวจสอบ CloudWatch logs ใน SageMaker console
- เช็ค ECR image และ training configuration
- ลอง instance type ที่เล็กกว่า

---

## 🎉 สรุป: การเทรนที่สำเร็จ

### ✅ สิ่งที่ได้
- **โมเดล CRNN** พร้อมใช้งานสำหรับตัวเลข 0-9
- **เวลาเทรน** เพียง 13 นาที (เร็วมาก!)
- **ค่าใช้จ่าย** เพียง $0.11 (ถูกมาก!)
- **Model artifacts** พร้อม deploy

### 🚀 Next Steps
1. **ทดสอบ** กับรูปตัวเลขจริงมากขึ้น
2. **Fine-tune** ด้วยข้อมูลคุณภาพสูง
3. **ขยาย** ไปยังตัวอักษรไทยเต็มรูปแบบ
4. **Deploy** เป็น SageMaker Endpoint

### 💡 Key Learnings
- **GPU instances** เร็วกว่าและคุ้มกว่า CPU สำหรับ deep learning
- **Manual approach** ให้ control และ monitoring ที่ดีกว่า automated scripts
- **Small dataset** สามารถเทรนได้เร็วและถูกมากบน cloud

---

**การเทรน Thai OCR บน SageMaker สำเร็จแล้ว!** 🎊

เอกสารนี้สะท้อนวิธีการจริงที่ทำงานได้ 100% จากประสบการณ์การเทรนจริง
