# Training Pipeline

This document outlines the training process for the Thai OCR model using PaddleOCR in both local and SageMaker environments.

## Local Training

1. **Prepare configuration**: Copy and modify a base config:
   ```bash
   cp PaddleOCR/configs/rec/rec_chinese_lite_train.yml configs/rec/thai_rec.yml
   ```
2. **Update character dictionary path** in `configs/rec/thai_rec.yml`:
   ```yaml
   Global:
     character_dict_path: ../../../th_dict.txt
   ```
3. **Run training**:
   ```bash
   python PaddleOCR/tools/train.py -c configs/rec/thai_rec.yml -o Global.epoch_num=50
   ```
4. **Monitor logs**: Check `logs/` directory or console output.

## SageMaker Training

1. **Upload training data** to S3:
   ```bash
   aws s3 cp train_data_thai_paddleocr_0724_1157/ s3://<bucket>/data/training/ --recursive
   ```
2. **Configure hyperparameters** in `hyperparameters.json`:
   ```json
   {
     "epoch_num": "50",
     "batch_size": "32",
     "learning_rate": "0.001"
   }
   ```
3. **Start training job** using Lambda or SageMaker SDK:
   ```python
   import boto3
   sm = boto3.client('sagemaker')
   sm.create_training_job(
     TrainingJobName='thai-ocr-job',
     AlgorithmSpecification={
       'TrainingImage': '<ECR_IMAGE_URI>',
       'TrainingInputMode': 'File'
     },
     InputDataConfig=[...],
     OutputDataConfig={...},
     ResourceConfig={...},
     HyperParameters={...}
   )
   ```
4. **Monitor job**:
   ```bash
   aws sagemaker describe-training-job --training-job-name thai-ocr-job
   ```
5. **Retrieve model artifacts** from S3.
