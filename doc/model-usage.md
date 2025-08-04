# 🎯 Thai OCR Model Usage Guide

This comprehensive guide covers how to use the trained Thai OCR model for inference, from basic single image testing to batch processing.

## 📋 Prerequisites

### Required Files
- ✅ **Trained Model**: `models/sagemaker_trained/best_model/model.pdparams`
- ✅ **Model Config**: `configs/rec/thai_rec_trained.yml`
- ✅ **Character Dictionary**: `thai-letters/th_dict.txt` (880 chars) or `th_dict_optimized.txt` (74 chars)
- ✅ **PaddleOCR Framework**: Installed in the environment

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Verify PaddleOCR installation
cd PaddleOCR
python -c "import paddle; print(f'Paddle version: {paddle.__version__}')"
```

## 🚀 Quick Start - Single Image Inference

### Method 1: Direct PaddleOCR Command (Recommended)

```bash
# Navigate to PaddleOCR directory
cd PaddleOCR

# Run inference on a single image
python tools/infer_rec.py \
  -c "../configs/rec/thai_rec_trained.yml" \
  -o Global.pretrained_model="../models/sagemaker_trained/best_model/model" \
  Global.infer_img="../path/to/your/image.jpg"
```

**Example with validation dataset**:
```bash
python tools/infer_rec.py \
  -c "../configs/rec/thai_rec_trained.yml" \
  -o Global.pretrained_model="../models/sagemaker_trained/best_model/model" \
  Global.infer_img="../thai-letters/datasets/converted/train_data_thai_paddleocr_0731_1604/train_data/rec/thai_data/val/346_01.jpg"
```

**Expected Output**:
```
[2025/08/04 10:45:41] ppocr INFO: infer_img: ../path/to/image.jpg
[2025/08/04 10:45:41] ppocr INFO:        result: อู๋DผณุมGลืรี๊ยวัณ์วั  0.0014090192271396518
[2025/08/04 10:45:41] ppocr INFO: success!
```

### Method 2: Python Script

```python
import subprocess
import os

def run_ocr_inference(image_path):
    """Run OCR inference on a single image"""
    cmd = [
        "python", "tools/infer_rec.py",
        "-c", "../configs/rec/thai_rec_trained.yml",
        "-o", 
        "Global.pretrained_model=../models/sagemaker_trained/best_model/model",
        f"Global.infer_img={image_path}"
    ]
    
    result = subprocess.run(cmd, 
                          capture_output=True, 
                          text=True, 
                          cwd="PaddleOCR")
    
    # Parse result
    if "result:" in result.stdout:
        prediction_line = result.stdout.split("result:")[1].split("\n")[0].strip()
        text, confidence = prediction_line.rsplit(" ", 1)
        return {
            "text": text.strip(),
            "confidence": float(confidence),
            "success": True
        }
    else:
        return {
            "error": result.stderr,
            "success": False
        }

# Example usage
result = run_ocr_inference("path/to/image.jpg")
if result["success"]:
    print(f"Predicted text: {result['text']}")
    print(f"Confidence: {result['confidence']:.6f}")
else:
    print(f"Error: {result['error']}")
```

## 📊 Batch Processing Multiple Images

### Script for Batch Testing
```python
import os
import subprocess
import json
from pathlib import Path

def batch_ocr_inference(image_directory, output_file=None):
    """Run OCR inference on all images in a directory"""
    results = []
    image_dir = Path(image_directory)
    
    # Supported image formats
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    for img_path in image_dir.iterdir():
        if img_path.suffix.lower() in supported_formats:
            print(f"Processing: {img_path.name}")
            
            # Run inference
            cmd = [
                "python", "tools/infer_rec.py",
                "-c", "../configs/rec/thai_rec_trained.yml",
                "-o", 
                "Global.pretrained_model=../models/sagemaker_trained/best_model/model",
                f"Global.infer_img={img_path}"
            ]
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  cwd="PaddleOCR")
            
            # Parse result
            if "result:" in result.stdout:
                prediction_line = result.stdout.split("result:")[1].split("\n")[0].strip()
                try:
                    text, confidence = prediction_line.rsplit(" ", 1)
                    results.append({
                        "image": img_path.name,
                        "predicted_text": text.strip(),
                        "confidence": float(confidence),
                        "success": True
                    })
                except ValueError:
                    results.append({
                        "image": img_path.name,
                        "predicted_text": prediction_line,
                        "confidence": 0.0,
                        "success": True
                    })
            else:
                results.append({
                    "image": img_path.name,
                    "error": result.stderr,
                    "success": False
                })
    
    # Save results
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {output_file}")
    
    return results

# Example usage
val_dir = "thai-letters/datasets/converted/train_data_thai_paddleocr_0731_1604/train_data/rec/thai_data/val"
results = batch_ocr_inference(val_dir, "batch_inference_results.json")

# Print summary
successful = sum(1 for r in results if r["success"])
print(f"\nProcessed {len(results)} images")
print(f"Successful: {successful}")
print(f"Failed: {len(results) - successful}")
```

## 🔧 Configuration Management

### Understanding the Configuration File
The `configs/rec/thai_rec_trained.yml` contains critical settings:

```yaml
Global:
  character_dict_path: ../thai-letters/th_dict.txt  # Character dictionary
  character_type: thai                              # Language type
  max_text_length: 25                              # Maximum prediction length
  use_space_char: false                            # Include space character

Architecture:
  algorithm: CRNN                                  # Model architecture
  model_type: rec                                  # Recognition model
  Backbone:
    name: MobileNetV3                              # Backbone network
    model_name: large
    scale: 0.5
  Neck:
    name: SequenceEncoder                          # Sequence encoder
    encoder_type: rnn
    hidden_size: 96
  Head:
    name: CTCHead                                  # CTC head for text recognition
    fc_decay: 0.00001

PostProcess:
  name: CTCLabelDecode                             # CTC label decoder
```

### Switching Between Dictionaries

**For current trained model (880 characters)**:
```yaml
Global:
  character_dict_path: ../thai-letters/th_dict.txt
```

**For optimized dictionary (74 characters) - requires retraining**:
```yaml
Global:
  character_dict_path: ../thai-letters/th_dict_optimized.txt
```

## 🐛 Troubleshooting Common Issues

### Issue 1: Dimension Mismatch Error
```
WARNING: The shape of model params head.fc.weight [192, 75] not matched 
with loaded params head.fc.weight [192, 882]
```
**Cause**: Dictionary size mismatch between training and inference
**Solution**: 
- Use the same dictionary that was used for training
- Current model requires `th_dict.txt` (880 chars)
- For `th_dict_optimized.txt`, retrain the model

### Issue 2: Image File Not Found
```
Exception: not found any img file in path/to/image.jpg
```
**Solutions**:
- Use absolute paths: `C:\full\path\to\image.jpg`
- Verify file exists: `ls path/to/image.jpg`
- Check image format (jpg, png, bmp supported)

### Issue 3: Model Loading Error
```
FileNotFoundError: model files not found
```
**Solutions**:
- Verify model files exist:
  ```bash
  ls models/sagemaker_trained/best_model/
  # Should show: model.pdparams, model.pdopt
  ```
- Check config path is correct
- Use relative paths from PaddleOCR directory

### Issue 4: Low Confidence Scores
**Current Model Characteristics**:
- Confidence typically 0.001-0.003 (very low)
- Often produces hallucinations (long incorrect text)
- Accuracy needs improvement

**Recommendations**:
- Use optimized dictionary for better results
- Consider retraining with better hyperparameters
- Validate input image quality

## 📈 Performance Analysis

### Current Model Performance
Based on testing with validation dataset:

| Metric | Value | Notes |
|--------|--------|-------|
| **Average Confidence** | 0.001-0.003 | Very low |
| **Accuracy** | Poor | Needs improvement |
| **Hallucination** | High | Generates irrelevant text |
| **Speed** | ~1-2 sec/image | CPU inference |

### Expected Output Examples

**Test Image 1**: `346_01.jpg`
- **Ground Truth**: `ตั่`
- **Model Output**: `อู๋DผณุมGลืรี๊ยวัณ์วั`
- **Confidence**: 0.0014
- **Status**: ❌ Incorrect (hallucination)

**Test Image 2**: `000_00.jpg`
- **Ground Truth**: `Z`
- **Model Output**: `"ปูปั้ปูภ้กีกู้Uบุ้สินั้วุ้Uวุ้สีภีวุ้`
- **Confidence**: 0.0015
- **Status**: ❌ Incorrect (hallucination)

## 🔄 Integration with Other Scripts

### With Model Testing Scripts
```bash
# Use comprehensive testing framework
python scripts/ml/comprehensive_test.py

# Use direct model testing
python scripts/testing/direct_model_test.py
```

### With Dataset Analysis
```bash
# Analyze dataset quality first
python scripts/testing/simple_dataset_test.py

# Then run model inference
python tools/infer_rec.py -c config.yml -o Global.infer_img=image.jpg
```

## 🎯 Best Practices

1. **Always run from PaddleOCR directory** for correct relative paths
2. **Use absolute paths** for image files to avoid path issues
3. **Verify configuration** matches training setup
4. **Check model files** exist before inference
5. **Monitor confidence scores** for quality assessment
6. **Use batch processing** for multiple images
7. **Save results** in JSON format for analysis
8. **Validate input images** are properly formatted

## 🔮 Future Improvements

1. **Retrain with optimized dictionary** (74 chars vs 880 chars)
2. **Implement data augmentation** during training
3. **Add preprocessing pipeline** for better image quality
4. **Optimize hyperparameters** for better convergence
5. **Add ensemble methods** for improved accuracy
6. **Implement confidence thresholding** to filter poor predictions

---

*This guide provides comprehensive instructions for using the trained Thai OCR model. For training new models, see [training.md](training.md). For deployment to production, see [deployment.md](deployment.md).*
