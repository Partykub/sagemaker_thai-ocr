# Model Deployment & Inference

This guide covers deploying the trained Thai OCR model and running inference both locally and on AWS SageMaker.

## Local Inference

1. **Install dependencies**:
   ```bash
   pip install paddleocr pillow opencv-python matplotlib
   ```
2. **Run inference script**:
   ```bash
   python inference.py --model-dir path/to/model --image path/to/image.jpg
   ```
3. **Inference script example**:
   ```python
   from paddleocr import PaddleOCR
   import cv2
   import matplotlib.pyplot as plt

   ocr = PaddleOCR(
     det_model_dir='model/det',
     rec_model_dir='model/rec',
     rec_char_dict_path='th_dict.txt',
     use_angle_cls=True
   )
   result = ocr.ocr('test.jpg', cls=True)
   # ...visualize results...
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
