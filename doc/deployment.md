# Model Deployment & Inference

This guide covers deploying the trained Thai OCR model and running inference both locally and on AWS SageMaker.

## 🎯 Local Model Inference (Quick Start)

### Prerequisites
1. **Trained model** available at `models/sagemaker_trained/best_model/`
2. **Configuration file** at `configs/rec/thai_rec_trained.yml`
3. **PaddleOCR installed** in the environment

### Step 1: Verify Model Structure
```bash
# Check model files exist
ls models/sagemaker_trained/best_model/
# Should contain: model.pdparams, model.pdopt, model.yml

# Check config file
ls configs/rec/thai_rec_trained.yml
```

### Step 2: Configure Model Settings
The config file `configs/rec/thai_rec_trained.yml` should contain:
```yaml
Global:
  character_dict_path: ../thai-letters/th_dict.txt  # Or th_dict_optimized.txt
  character_type: thai
  max_text_length: 25
  use_space_char: false

Architecture:
  algorithm: CRNN
  model_type: rec
  Backbone:
    name: MobileNetV3
    model_name: large
    scale: 0.5
  Neck:
    name: SequenceEncoder
    encoder_type: rnn
    hidden_size: 96
  Head:
    name: CTCHead
    fc_decay: 0.00001

PostProcess:
  name: CTCLabelDecode
```

### Step 3: Run Direct Model Inference
```bash
# Navigate to PaddleOCR directory
cd PaddleOCR

# Run inference on a single image
python tools/infer_rec.py \
  -c "../configs/rec/thai_rec_trained.yml" \
  -o Global.pretrained_model="../models/sagemaker_trained/best_model/model" \
  Global.infer_img="path/to/your/image.jpg"

# Example with validation images
python tools/infer_rec.py \
  -c "../configs/rec/thai_rec_trained.yml" \
  -o Global.pretrained_model="../models/sagemaker_trained/best_model/model" \
  Global.infer_img="../thai-letters/datasets/converted/train_data_thai_paddleocr_0731_1604/train_data/rec/thai_data/val/346_01.jpg"
```

### Step 4: Expected Output Format
```
[2025/08/04 10:45:41] ppocr INFO: infer_img: ../path/to/image.jpg
[2025/08/04 10:45:41] ppocr INFO:        result: อู๋DผณุมGลืรี๊ยวัณ์วั  0.0014090192271396518
[2025/08/04 10:45:41] ppocr INFO: success!
```

### Troubleshooting Common Issues

#### Issue 1: Dimension Mismatch Error
```
WARNING: The shape of model params head.fc.weight [192, 75] not matched with loaded params head.fc.weight [192, 882]
```
**Solution**: Ensure the `character_dict_path` matches the training dictionary:
- Use `th_dict.txt` (880 chars) for the current trained model
- Or retrain with `th_dict_optimized.txt` (74 chars) for better accuracy

#### Issue 2: Image File Not Found
```
Exception: not found any img file in path
```
**Solution**: Use absolute paths for image files or ensure relative paths are correct from PaddleOCR directory.

#### Issue 3: Model Files Missing
```
FileNotFoundError: model files not found
```
**Solution**: Verify model structure:
```bash
# Should exist:
models/sagemaker_trained/best_model/model.pdparams
models/sagemaker_trained/best_model/model.pdopt
```

### Performance Notes
- **Current model accuracy**: Low (needs improvement)
- **Confidence scores**: Typically 0.001-0.003 (very low)
- **Common issues**: Hallucination (generating long incorrect text)
- **Recommended**: Use optimized dictionary for better results

## 📊 Batch Testing Multiple Images

### Create a Test Script
```python
import os
import subprocess
import json

def test_model_on_validation_set():
    val_dir = "thai-letters/datasets/converted/train_data_thai_paddleocr_0731_1604/train_data/rec/thai_data/val"
    results = []
    
    # Test first 10 images
    for img_file in os.listdir(val_dir)[:10]:
        if img_file.endswith('.jpg'):
            img_path = os.path.join(val_dir, img_file)
            
            # Run inference
            cmd = [
                "python", "tools/infer_rec.py",
                "-c", "../configs/rec/thai_rec_trained.yml",
                "-o", 
                "Global.pretrained_model=../models/sagemaker_trained/best_model/model",
                f"Global.infer_img={img_path}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd="PaddleOCR")
            
            # Parse result
            if "result:" in result.stdout:
                prediction = result.stdout.split("result:")[1].split("\n")[0].strip()
                results.append({
                    "image": img_file,
                    "prediction": prediction
                })
    
    return results

# Run batch test
results = test_model_on_validation_set()
print(json.dumps(results, indent=2, ensure_ascii=False))
```

### Method 1: PaddleOCR Python API
```bash
pip install paddleocr pillow opencv-python matplotlib
```

```python
from paddleocr import PaddleOCR
import cv2
import matplotlib.pyplot as plt

# Note: This method may not work with custom trained models
ocr = PaddleOCR(
  det_model_dir='model/det',
  rec_model_dir='model/rec', 
  rec_char_dict_path='th_dict.txt',
  use_angle_cls=True
)
result = ocr.ocr('test.jpg', cls=True)
```

### Method 2: Custom Inference Script
```python
import paddle
from ppocr.modeling.architectures import build_model
from ppocr.postprocess import build_post_process
from ppocr.utils.save_load import load_model
import cv2
import numpy as np

# Load trained model
config = load_config('configs/rec/thai_rec_trained.yml')
model = build_model(config['Architecture'])
load_model(config, model, model_path='models/sagemaker_trained/best_model')

# Preprocessing
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    # Add preprocessing steps based on training config
    return img

# Run inference
img = preprocess_image('test.jpg')
preds = model(img)
result = post_process(preds)
print(result)
```

## SageMaker Inference

1. **Create SageMaker Model**:
   ```bash
   aws sagemaker create-model \
     --model-name thai-ocr-model \
     --primary-container Image=<ECR_IMAGE_URI>,ModelDataUrl=s3://<bucket>/models/model.tar.gz \
     --execution-role-arn <SAGEMAKER_ROLE>
   ```
2. **Create Endpoint Configuration**:
   ```bash
   aws sagemaker create-endpoint-config \
     --endpoint-config-name thai-ocr-config \
     --production-variants VariantName=AllTraffic,ModelName=thai-ocr-model,InstanceType=ml.m5.large,InitialInstanceCount=1
   ```
3. **Deploy Endpoint**:
   ```bash
   aws sagemaker create-endpoint \
     --endpoint-name thai-ocr-endpoint \
     --endpoint-config-name thai-ocr-config
   ```
4. **Invoke Endpoint** with SDK:
   ```python
   import boto3
   runtime = boto3.client('sagemaker-runtime')
   with open('image.jpg', 'rb') as f:
       payload = f.read()
   response = runtime.invoke_endpoint(
     EndpointName='thai-ocr-endpoint',
     ContentType='application/octet-stream',
     Body=payload
   )
   print(response['Body'].read())
   ```
