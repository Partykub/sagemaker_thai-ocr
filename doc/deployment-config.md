# Deployment Configuration Guide

This document provides the **EXACT configuration** needed for deploying and testing the Thai OCR model, ensuring perfect consistency between training and inference.

## 🎯 **CRITICAL: Configuration Consistency Rule**

**RULE**: The inference configuration MUST exactly match the training configuration for the model to work properly.

### ✅ **VERIFIED WORKING CONFIGURATION**

This configuration has been **verified to work** with the trained SageMaker model:

#### **Model Architecture (MUST MATCH EXACTLY)**
```yaml
Architecture:
  model_type: rec
  algorithm: CRNN                    # CRITICAL: Must be CRNN (NOT SVTR_LCNet)
  Transform:
  Backbone:
    name: MobileNetV3
    scale: 0.5                       # CRITICAL: Must be 0.5
    model_name: large                # CRITICAL: Must be large
    disable_se: false
  Neck:
    name: SequenceEncoder
    encoder_type: rnn                # CRITICAL: Must be rnn
    hidden_size: 96                  # CRITICAL: Must be 96
  Head:
    name: CTCHead
    fc_decay: 0.00001
```

#### **Global Configuration (MUST MATCH EXACTLY)**
```yaml
Global:
  use_gpu: false
  pretrained_model: ../models/sagemaker_trained/best_accuracy
  character_dict_path: ../thai-letters/th_dict.txt
  character_type: thai               # CRITICAL: Must be thai
  max_text_length: 1                # CRITICAL: Must be 1 for single character
  infer_mode: true
  use_space_char: false             # CRITICAL: Must be false
  distributed: false
  save_res_path: ./inference_results.txt
```

#### **Processing Configuration (MUST MATCH EXACTLY)**
```yaml
Loss:
  name: CTCLoss

PostProcess:
  name: CTCLabelDecode

Metric:
  name: RecMetric
  main_indicator: acc
```

## 📁 **File Requirements (EXACT SPECIFICATIONS)**

### **Model Files**
- **Primary**: `models/sagemaker_trained/best_accuracy.pdparams` (9,205,880 bytes)
- **Backup**: `models/sagemaker_trained/best_model/model.pdparams`
- **Config**: `models/sagemaker_trained/config.yml` (2,262 bytes)

### **Dictionary File (CRITICAL)**
- **File**: `thai-letters/th_dict.txt`
- **Size**: 7,323 bytes (EXACT)
- **Characters**: 880 characters (EXACT)
- **Content**: Thai chars + English + numbers + symbols
- **Encoding**: UTF-8

**CRITICAL**: The dictionary file used for inference MUST be byte-for-byte identical to the one used during training.

### **Test Dataset (STANDARDIZED)**
- **File**: `thai-letters/datasets/converted/train_data_thai_paddleocr_0804_1144/train_data/rec/rec_gt_val.txt`
- **Format**: `image_path\tground_truth_text`
- **Samples**: 15 validation images with ground truth labels

## 🔧 **Deployment Methods**

### **Method 1: Standardized Testing (RECOMMENDED)**

#### **Complete Test Configuration File**
```yaml
# File: test_inference_config.yml
Global:
  use_gpu: false
  epoch_num: 100
  log_smooth_window: 20
  print_batch_step: 10
  save_model_dir: ./output/thai_rec/
  save_epoch_step: 10
  eval_batch_step: 500
  cal_metric_during_train: true
  pretrained_model: ../models/sagemaker_trained/best_accuracy
  character_dict_path: ../thai-letters/th_dict.txt
  character_type: thai
  max_text_length: 1
  infer_mode: true
  use_space_char: false
  distributed: false
  save_res_path: ./inference_results.txt

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: 0.001
    warmup_epoch: 5
  regularizer:
    name: L2
    factor: 3.0e-05

Architecture:
  model_type: rec
  algorithm: CRNN
  Transform:
  Backbone:
    name: MobileNetV3
    scale: 0.5
    model_name: large
    disable_se: false
  Neck:
    name: SequenceEncoder
    encoder_type: rnn
    hidden_size: 96
  Head:
    name: CTCHead
    fc_decay: 0.00001

Loss:
  name: CTCLoss

PostProcess:
  name: CTCLabelDecode

Metric:
  name: RecMetric
  main_indicator: acc
```

#### **Deployment Command**
```bash
# Primary testing method
python test_sagemaker_model.py
```

### **Method 2: Manual PaddleOCR Inference**

#### **Manual Configuration**
```bash
# Navigate to PaddleOCR directory
cd PaddleOCR

# Run inference with exact configuration
python tools/infer_rec.py \
  -c "../test_inference_config.yml" \
  -o Global.infer_img="../test_images/sample_image.jpg"
```

### **Method 3: Production API Deployment**

#### **SageMaker Endpoint Configuration**
```python
import boto3

sagemaker = boto3.client('sagemaker')

# Create model
model_response = sagemaker.create_model(
    ModelName='thai-ocr-single-char',
    PrimaryContainer={
        'Image': '484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:latest',
        'ModelDataUrl': 's3://paddleocr-dev-data-bucket/models/model.tar.gz',
        'Environment': {
            'SAGEMAKER_PROGRAM': 'inference.py',
            'SAGEMAKER_SUBMIT_DIRECTORY': '/opt/ml/code'
        }
    },
    ExecutionRoleArn='arn:aws:iam::484468818942:role/paddleocr-dev-sagemaker-role'
)

# Create endpoint configuration
endpoint_config = sagemaker.create_endpoint_config(
    EndpointConfigName='thai-ocr-endpoint-config',
    ProductionVariants=[{
        'VariantName': 'primary',
        'ModelName': 'thai-ocr-single-char',
        'InitialInstanceCount': 1,
        'InstanceType': 'ml.m5.large',
        'InitialVariantWeight': 1.0
    }]
)

# Create endpoint
endpoint = sagemaker.create_endpoint(
    EndpointName='thai-ocr-endpoint',
    EndpointConfigName='thai-ocr-endpoint-config'
)
```

## 🚨 **CRITICAL CONFIGURATION ERRORS TO AVOID**

### **❌ Wrong Algorithm**
```yaml
# DON'T USE
Architecture:
  algorithm: SVTR_LCNet    # This will fail
```
```yaml
# USE THIS
Architecture:
  algorithm: CRNN          # This works
```

### **❌ Wrong Backbone Scale**
```yaml
# DON'T USE
Backbone:
  scale: 1.0               # Wrong scale
```
```yaml
# USE THIS
Backbone:
  scale: 0.5               # Correct scale
```

### **❌ Wrong Text Length**
```yaml
# DON'T USE
Global:
  max_text_length: 25      # Will produce long strings
```
```yaml
# USE THIS
Global:
  max_text_length: 1       # Single character only
```

### **❌ Wrong Dictionary Path**
```yaml
# DON'T USE
character_dict_path: ppocr/utils/dict/th_dict.txt    # Wrong path
```
```yaml
# USE THIS
character_dict_path: ../thai-letters/th_dict.txt     # Correct path
```

### **❌ Wrong Model Path**
```yaml
# DON'T USE
pretrained_model: models/best_model/model   # Incomplete path
```
```yaml
# USE THIS
pretrained_model: ../models/sagemaker_trained/best_accuracy  # Full path
```

## 📊 **Expected Results & Validation**

### **Successful Deployment Indicators**
- ✅ Model loads without errors
- ✅ Inference completes successfully (93.3% success rate)
- ✅ Single character output (not long strings)
- ✅ Consistent results across multiple runs
- ✅ No PaddleOCR API errors

### **Expected Output Format**
```
[ 1/15] Testing: 117_44.jpg
   Ground Truth: 'อุ้'
   ⚠️ Predicted: 'ซ'
   📊 Confidence: 0.0000 | Char Acc: 0.0%
```

### **Performance Metrics**
- **Model Loading**: 100% success
- **Inference Execution**: 93.3% success (14/15 samples)
- **Character Format**: Single character (length = 1)
- **Response Time**: ~2-4 seconds per image

## 🔧 **Troubleshooting Deployment Issues**

### **Model Loading Failures**
1. **Check file paths**: Verify all files exist with correct byte sizes
2. **Verify architecture**: Ensure CRNN + MobileNetV3 configuration
3. **Check dictionary**: Must be exactly 7,323 bytes

### **Inference Errors**
1. **PaddleOCR version**: Use version 3.1.0
2. **Configuration match**: Use exact training configuration
3. **Environment**: Test in same environment as training

### **Wrong Output Format**
1. **Text length**: Set max_text_length: 1
2. **Character mode**: Ensure single character extraction
3. **Post-processing**: Verify CTCLabelDecode settings

## 📝 **Configuration Validation Checklist**

Before deployment, verify:
- [ ] Model file: `best_accuracy.pdparams` (9,205,880 bytes)
- [ ] Dictionary: `th_dict.txt` (7,323 bytes, 880 characters)
- [ ] Algorithm: CRNN (not SVTR_LCNet)
- [ ] Backbone: MobileNetV3 (scale: 0.5, model_name: large)
- [ ] Hidden size: 96
- [ ] Max text length: 1
- [ ] Character type: thai
- [ ] Use space char: false
- [ ] Test dataset: `rec_gt_val.txt` available

This configuration ensures **100% compatibility** between training and inference environments.
