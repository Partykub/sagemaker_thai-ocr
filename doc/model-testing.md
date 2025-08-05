# Model Testing & Inference Guide

This document provides the **standardized testing procedure** for the Thai OCR model, ensuring consistency between training and inference configurations.

## 🎯 STANDARDIZED TESTING CONFIGURATION

### ✅ **Verified Working Configuration**

#### **Model Files (MUST USE THESE EXACTLY)**
- **Primary Model**: `models/sagemaker_trained/best_accuracy.pdparams` (9,205,880 bytes)
- **Alternative**: `models/sagemaker_trained/best_model/model.pdparams`
- **Config Reference**: `models/sagemaker_trained/config.yml` (2,262 bytes)

#### **Dictionary (MUST BE IDENTICAL TO TRAINING)**
- **File**: `thai-letters/th_dict.txt`
- **Size**: 7,323 bytes (880 characters)
- **Content**: Thai characters, English letters, numbers, symbols
- **Critical**: This MUST be the exact same file used during training

#### **Architecture (MUST MATCH TRAINING EXACTLY)**
```yaml
Architecture:
  model_type: rec
  algorithm: CRNN                  # EXACT MATCH with training
  Backbone:
    name: MobileNetV3
    scale: 0.5
    model_name: large              # EXACT MATCH with training
  Neck:
    name: SequenceEncoder
    encoder_type: rnn              # EXACT MATCH with training
    hidden_size: 96                # EXACT MATCH with training
  Head:
    name: CTCHead
    fc_decay: 0.00001

PostProcess:
  name: CTCLabelDecode
```

#### **Global Configuration (MUST MATCH TRAINING)**
```yaml
Global:
  use_gpu: false
  pretrained_model: ../models/sagemaker_trained/best_accuracy
  character_dict_path: ../thai-letters/th_dict.txt
  character_type: thai
  max_text_length: 1               # SINGLE CHARACTER MODE
  infer_mode: true                 # Inference mode
  use_space_char: false
  save_res_path: ./inference_results.txt
```

## 🧪 **STANDARD TESTING PROCEDURES**

### **Method 1: Automated Testing (RECOMMENDED)**

#### **Primary Test Script**
```bash
# Use the standardized test script
python test_sagemaker_model.py
```

**This script automatically:**
- Uses the exact training configuration
- Tests with validation dataset (ground truth available)
- Provides detailed accuracy metrics
- Saves results to JSON file

#### **Test Dataset (STANDARDIZED)**
- **Location**: `thai-letters/datasets/converted/train_data_thai_paddleocr_0804_1144/train_data/rec/rec_gt_val.txt`
- **Format**: Tab-separated `image_path\tground_truth_text`
- **Sample Count**: 15 validation samples
- **Examples**:
  ```
  thai_data/val/117_44.jpg	อุ้
  thai_data/val/032_34.jpg	ค์
  thai_data/val/121_15.jpg	ขั้
  thai_data/val/488_55.jpg	อิ
  thai_data/val/291_42.jpg	ท๊
  ```

#### **Expected Output Format**
```
[ 1/15] Testing: 117_44.jpg
   Ground Truth: 'อุ้'
   ⚠️ Predicted: 'ซ'
   📊 Confidence: 0.0000 | Char Acc: 0.0%
```

### **Method 2: Manual Single Image Testing**

#### **Manual Testing Command**
```bash
# Navigate to PaddleOCR directory
cd PaddleOCR

# Create inference config (or use existing test_inference_config.yml)
python tools/infer_rec.py \
  -c "../test_inference_config.yml" \
  -o Global.infer_img="../test_images/thai_word_01_สวัสดี.jpg"
```

#### **Expected Single Image Output**
```
result: ซ 0.0012747200671583414
```
- First character is the prediction
- Number is the confidence score

### **Method 3: Batch Testing with Custom Images**

#### **Test Multiple Images**
```python
import subprocess
from pathlib import Path

def test_custom_images(image_dir):
    images = list(Path(image_dir).glob("*.jpg"))
    
    for img in images:
        cmd = [
            "python", "PaddleOCR/tools/infer_rec.py",
            "-c", "test_inference_config.yml",
            "-o", f"Global.infer_img={img}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"{img.name}: {result.stdout}")
```

## 📊 **PERFORMANCE METRICS & INTERPRETATION**

### **Current Verified Performance**
- **Model Loading Success**: 100% ✅
- **Inference Execution**: 93.3% ✅ (14/15 samples)
- **Single Character Output**: Working ✅
- **Accuracy**: Low (needs improvement) ⚠️

### **Sample Test Results (Current)**
```
Ground Truth → Predicted
อุ้ → ซ
ค์ → (error)
ขั้ → ย
อิ → ว
ท๊ → พ
ผ้ → ย
กํ → น
ค → ช
จิ → ก
หั → l
ซ์ → -
มั๊ → €
รี๊ → m
สํ → ค
กั๋ → ต
```

### **Success Indicators**
- ✅ Model loads without errors
- ✅ Inference completes successfully
- ✅ Single character output (not long strings)
- ✅ Consistent results across runs

### **Areas for Improvement**
- ❌ Character accuracy (predictions don't match ground truth)
- ❌ Confidence scores (very low, near 0.0)
- ❌ Some inference errors (1 out of 15 samples)

## 🔧 **TROUBLESHOOTING TESTING ISSUES**

### **Common Testing Problems & Solutions**

#### **Problem 1: Model Loading Errors**
```
Error: FileNotFoundError: model.pdparams not found
```
**Solution**: Use correct model path
```yaml
# Correct paths
pretrained_model: ../models/sagemaker_trained/best_accuracy
# OR
pretrained_model: ../models/sagemaker_trained/best_model/model
```

#### **Problem 2: Dictionary Errors**
```
Error: character_dict_path file not found
```
**Solution**: Verify dictionary file exists
```bash
# Check dictionary
ls -la thai-letters/th_dict.txt
# Should show: 7,323 bytes
```

#### **Problem 3: Architecture Mismatch**
```
Error: Model structure mismatch
```
**Solution**: Use EXACTLY the same architecture as training
- Algorithm: CRNN (NOT SVTR_LCNet)
- Backbone: MobileNetV3 (scale: 0.5, model_name: large)
- Hidden size: 96

#### **Problem 4: Inference Hangs or Crashes**
```bash
# Check PaddleOCR version
python -c "import paddleocr; print(paddleocr.__version__)"
# Should show: 3.1.0
```

#### **Problem 5: Wrong Output Format**
If getting long text instead of single characters:
```yaml
# Ensure in config
max_text_length: 1  # NOT 25
```

### **Configuration Validation Checklist**

Before running tests, verify:
- [ ] Model file exists and is ~9MB
- [ ] Dictionary file is exactly 7,323 bytes
- [ ] Config uses CRNN (not SVTR_LCNet)
- [ ] max_text_length: 1
- [ ] character_type: thai
- [ ] use_space_char: false

## 📝 **TEST RESULT DOCUMENTATION**

### **Standard Test Report Format**
```json
{
  "timestamp": "20250805_154608",
  "config_used": "test_inference_config.yml",
  "model_path": "models/sagemaker_trained/best_accuracy",
  "dictionary": "thai-letters/th_dict.txt",
  "test_results": {
    "total_samples": 15,
    "successful_inferences": 14,
    "success_rate": 0.933,
    "average_character_accuracy": 0.0,
    "exact_match_rate": 0.0
  },
  "detailed_results": [...]
}
```

### **Results Analysis**
- **Success Rate > 90%**: Model loading and inference working
- **Character Accuracy < 50%**: Model needs retraining or different approach
- **Confidence Scores < 0.1**: Model uncertain about predictions
- **Exact Match Rate = 0%**: No perfect predictions

## 🎯 **NEXT STEPS FOR IMPROVEMENT**

### **If Model Works but Accuracy is Low**
1. **Retrain with Single Character Data**: Use `scripts/easy_single_char_training.py`
2. **Adjust Dictionary**: Try smaller, focused Thai character set
3. **Improve Preprocessing**: Adjust image size, normalization
4. **More Training Data**: Generate more diverse Thai character images

### **If Model Loading Fails**
1. **Check File Paths**: Verify all files exist with correct sizes
2. **Architecture Match**: Ensure exact same config as training
3. **Version Compatibility**: Use same PaddleOCR version as training
4. **Container Testing**: Test in Docker environment similar to training

### **Testing Different Model Configurations**
```bash
# Test with different model files
python test_sagemaker_model.py --model best_accuracy.pdparams
python test_sagemaker_model.py --model latest.pdparams
python test_sagemaker_model.py --model iter_epoch_45.pdparams
```

This standardized testing approach ensures consistency and helps identify specific issues with the trained model.
