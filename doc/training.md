# Training Pipeline

This document outlines the training process for the Thai OCR model using PaddleOCR in both local and SageMaker environments.

## Prerequisites

Before starting training, ensure you have:
- Completed data preparation (see [dataset.md](dataset.md))
- Configured AWS permissions (see [installation.md](installation.md))
- Set up training configurations

## Training Configuration Setup

### Automated Configuration Setup
Use the automated script to set up multiple training configurations:

```bash
# Run Task 3: Configuration setup
python scripts/training/setup_training_config.py
```

This creates three configurations:
- `configs/rec/thai_rec_dev.yml`: 10 epochs for quick testing
- `configs/rec/thai_rec.yml`: 100 epochs for main training  
- `configs/rec/thai_rec_prod.yml`: 200 epochs for production

### Manual Configuration
If you need custom configurations:

1. **Base configuration**: Start with PaddleOCR's recognition config
2. **Update paths**: Set correct data directories and dictionary paths
3. **Thai-specific settings**:
   ```yaml
   Global:
     character_dict_path: ppocr/utils/dict/th_dict.txt
     character_type: th
     max_text_length: 25
     use_space_char: true
   ```

## Local Training

### Quick Development Training
```bash
# Test with minimal epochs for development
python PaddleOCR/tools/train.py -c configs/rec/thai_rec_dev.yml
```

### Full Local Training
```bash
# Main training configuration
python PaddleOCR/tools/train.py -c configs/rec/thai_rec.yml

# With custom parameters
python PaddleOCR/tools/train.py -c configs/rec/thai_rec.yml \
  -o Global.epoch_num=50 \
  -o Global.save_epoch_step=10 \
  -o Optimizer.lr.learning_rate=0.001
```

### Local Training Requirements
- **Memory**: 8GB+ RAM recommended
- **Storage**: 10GB+ free space for model checkpoints
- **Python environment**: All dependencies from requirements.txt

## SageMaker Training

### Quick SageMaker Deployment
The easiest way to train on SageMaker:

```bash
# Complete automated deployment
python scripts/continue_deployment_v2.py
```

This script:
1. Builds Docker image with all dependencies
2. Pushes to ECR repository  
3. Creates SageMaker training job
4. Monitors training progress

### Manual SageMaker Setup

#### 1. Prepare Docker Container
```bash
# Build container with dependencies
docker build -f Dockerfile.sagemaker -t thai-ocr .

# Tag and push to ECR
aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin 484468818942.dkr.ecr.ap-southeast-1.amazonaws.com
docker tag thai-ocr:latest 484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:latest
docker push 484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:latest
```

#### 2. Upload Training Data
```bash
# Upload converted dataset to S3
aws s3 cp train_data_thai_paddleocr_v1/ s3://paddleocr-dev-data-bucket/data/training/ --recursive
```

#### 3. Create Training Job
```python
import boto3

sagemaker = boto3.client('sagemaker')
training_job = sagemaker.create_training_job(
    TrainingJobName='paddleocr-thai-training-{timestamp}',
    AlgorithmSpecification={
        'TrainingImage': '484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:latest',
        'TrainingInputMode': 'File'
    },
    RoleArn='arn:aws:iam::484468818942:role/paddleocr-dev-sagemaker-role',
    InputDataConfig=[{
        'ChannelName': 'training',
        'DataSource': {
            'S3DataSource': {
                'S3DataType': 'S3Prefix',
                'S3Uri': 's3://paddleocr-dev-data-bucket/data/training/',
                'S3DataDistributionType': 'FullyReplicated'
            }
        }
    }],
    OutputDataConfig={
        'S3OutputPath': 's3://paddleocr-dev-data-bucket/models/'
    },
    ResourceConfig={
        'InstanceType': 'ml.m5.large',
        'InstanceCount': 1,
        'VolumeSizeInGB': 30
    },
    StoppingCondition={
        'MaxRuntimeInSeconds': 86400  # 24 hours
    },
    HyperParameters={
        'epochs': '50',
        'learning_rate': '0.001'
    }
)
```

### SageMaker Training Monitoring

#### Real-time Progress Monitoring
```bash
# Monitor training job status
aws sagemaker describe-training-job --training-job-name paddleocr-thai-training-{job-id}

# Watch CloudWatch logs  
aws logs tail /aws/sagemaker/TrainingJobs --follow

# Check specific log stream
aws logs get-log-events --log-group-name /aws/sagemaker/TrainingJobs \
  --log-stream-name paddleocr-thai-training-{job-id}/algo-1-{timestamp}
```

#### Training Status Check Script
```bash
# Continuous monitoring
while true; do
    aws sagemaker describe-training-job --training-job-name paddleocr-thai-training-{job-id} \
      --query "{Status: TrainingJobStatus, Secondary: SecondaryStatus, Time: TrainingTimeInSeconds}"
    sleep 30
done
```

## Training Configuration Reference

### Key Configuration Parameters

```yaml
Global:
  use_gpu: false                    # Set to false for SageMaker CPU instances
  distributed: false               # Disable for SageMaker compatibility
  epoch_num: 100                   # Number of training epochs
  log_smooth_window: 20            # Logging window size
  print_batch_step: 10             # Print progress every N batches
  save_model_dir: ./output/thai_rec/  # Model output directory
  save_epoch_step: 10              # Save checkpoint every N epochs
  eval_batch_step: 500             # Evaluation frequency
  character_dict_path: ppocr/utils/dict/th_dict.txt  # Thai character dictionary
  character_type: th               # Thai language setting
  max_text_length: 25              # Maximum text length for recognition
  use_space_char: true             # Include space character in recognition

Train:
  dataset:
    name: SimpleDataSet
    data_dir: /opt/ml/input/data/training/rec/  # SageMaker training data path
    label_file_list: 
      - /opt/ml/input/data/training/rec/rec_gt_train.txt
  loader:
    shuffle: true
    batch_size_per_card: 256
    drop_last: false
    num_workers: 8

Eval:
  dataset:
    name: SimpleDataSet  
    data_dir: /opt/ml/input/data/training/rec/
    label_file_list:
      - /opt/ml/input/data/training/rec/rec_gt_val.txt
  loader:
    shuffle: false
    drop_last: false
    batch_size_per_card: 256
    num_workers: 8

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: 0.001
    warmup_epoch: 5

Architecture:
  model_type: rec
  algorithm: SVTR_LCNet
  Backbone:
    name: SVTRNet
    img_size: [64, 256]
    out_char_num: 25
    out_channels: 192
```

### Environment-Specific Configurations

#### Development (thai_rec_dev.yml)
- **Epochs**: 10 (quick testing)
- **Batch size**: 128
- **Learning rate**: 0.001
- **Use case**: Local development and testing

#### Production (thai_rec.yml)  
- **Epochs**: 100 (main training)
- **Batch size**: 256
- **Learning rate**: 0.001
- **Use case**: Standard training runs

#### Production Extended (thai_rec_prod.yml)
- **Epochs**: 200 (extended training)
- **Batch size**: 256  
- **Learning rate**: 0.0005 (reduced for stability)
- **Use case**: Final production models

## Troubleshooting Training Issues

### Common Training Problems

#### Dependency Issues
- **Error**: `ModuleNotFoundError: No module named 'skimage'`
- **Solution**: Update requirements.txt with `scikit-image>=0.19.0`

- **Error**: `ModuleNotFoundError: No module named 'rapidfuzz'`  
- **Solution**: Add `rapidfuzz>=2.0.0` to requirements.txt

#### Docker Issues
- **Error**: `ImportError: libGL.so.1: cannot open shared object file`
- **Solution**: Add `libgl1-mesa-glx` to Dockerfile system packages

#### PaddleOCR Configuration Issues
- **Error**: `AttributeError: 'NoneType' object has no attribute 'distributed'`
- **Solution**: Set `distributed: false` in training config

#### Data Path Issues
- **Error**: `FileNotFoundError: rec_gt_train.txt`
- **Solution**: Verify S3 data structure and update `data_dir` paths

#### Memory Issues
- **Error**: Out of memory during training
- **Solutions**:
  - Reduce batch size in config
  - Use smaller instance type for development
  - Enable gradient accumulation

### Performance Optimization

#### Training Speed
- **Use appropriate instance types**: ml.m5.large for development, ml.c5.xlarge for production
- **Optimize batch size**: Balance between memory usage and training speed
- **Enable parallel data loading**: Set `num_workers: 8` in data loaders

#### Model Quality
- **Learning rate scheduling**: Use Cosine decay for stable convergence
- **Data augmentation**: Enable in dataset configuration
- **Early stopping**: Monitor validation metrics

## Output and Model Artifacts

### Local Training Output
```
output/thai_rec/
├── best_accuracy.pdparams      # Best model parameters
├── best_accuracy.pdopt         # Optimizer state
├── config.yml                  # Training configuration
├── train.log                   # Training logs
└── iter_epoch_{N}.pdparams     # Epoch checkpoints
```

### SageMaker Training Output
Models are automatically uploaded to S3:
```
s3://paddleocr-dev-data-bucket/models/{job-name}/
├── output/
│   └── model.tar.gz           # Compressed model artifacts
└── debug-output/              # Training logs and debug info
```

### Model Evaluation
```bash
# Evaluate trained model
python PaddleOCR/tools/eval.py -c configs/rec/thai_rec.yml \
  -o Global.pretrained_model=./output/thai_rec/best_accuracy
```

This will output metrics like:
- Character accuracy
- Word accuracy  
- Edit distance
- Recognition performance on test set
