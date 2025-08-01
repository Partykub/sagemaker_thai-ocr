#!/usr/bin/env python3
"""
SageMaker Training Script for Thai OCR
Entry point for SageMaker training jobs
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Add PaddleOCR to Python path
sys.path.insert(0, '/opt/ml/code/PaddleOCR')

def setup_logging():
    """Setup logging for SageMaker"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def parse_hyperparameters():
    """Parse hyperparameters from SageMaker"""
    parser = argparse.ArgumentParser()
    
    # SageMaker specific arguments
    parser.add_argument('--model-dir', type=str, default='/opt/ml/model')
    parser.add_argument('--train', type=str, default='/opt/ml/input/data/training')
    parser.add_argument('--config', type=str, default='thai_rec_sagemaker.yml')
    
    # Training hyperparameters
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument('--learning-rate', type=float, default=0.001)
    parser.add_argument('--use-gpu', type=bool, default=True)
    
    # Handle SageMaker's way of passing arguments
    args, unknown = parser.parse_known_args()
    
    # Log hyperparameters
    logger = logging.getLogger(__name__)
    logger.info(f"Training arguments: {vars(args)}")
    if unknown:
        logger.warning(f"Unknown arguments ignored: {unknown}")
    
    return args

def update_config_for_sagemaker(config_path, args):
    """Update config file with SageMaker paths and hyperparameters"""
    import yaml
    
    logger = logging.getLogger(__name__)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Update paths for SageMaker
    config['Global']['save_model_dir'] = args.model_dir + '/'
    config['Global']['save_inference_dir'] = args.model_dir + '/inference/'
    config['Global']['character_dict_path'] = os.path.join(args.train, 'th_dict.txt')
    config['Global']['epoch_num'] = args.epochs
    config['Global']['use_gpu'] = False  # Disable GPU for CPU instance
    config['Global']['distributed'] = False  # Disable distributed training
    
    # Update dataset paths
    config['Train']['dataset']['data_dir'] = os.path.join(args.train, 'rec') + '/'
    config['Train']['dataset']['label_file_list'] = [os.path.join(args.train, 'rec/rec_gt_train.txt')]
    config['Train']['loader']['batch_size_per_card'] = args.batch_size
    
    config['Eval']['dataset']['data_dir'] = os.path.join(args.train, 'rec') + '/'
    config['Eval']['dataset']['label_file_list'] = [os.path.join(args.train, 'rec/rec_gt_val.txt')]
    config['Eval']['loader']['batch_size_per_card'] = args.batch_size
    
    # Update learning rate
    config['Optimizer']['lr']['learning_rate'] = args.learning_rate
    
    # Save updated config
    updated_config_path = '/opt/ml/code/sagemaker_config.yml'
    with open(updated_config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    logger.info(f"Updated config saved to: {updated_config_path}")
    return updated_config_path

def main():
    """Main training function"""
    logger = setup_logging()
    logger.info("Starting SageMaker Thai OCR Training")
    
    # Parse arguments
    args = parse_hyperparameters()
    
    # Check data directory
    train_dir = Path(args.train)
    if not train_dir.exists():
        raise FileNotFoundError(f"Training data directory not found: {train_dir}")
    
    logger.info(f"Training data directory: {train_dir}")
    logger.info(f"Files in training dir: {list(train_dir.rglob('*'))}")
    
    # Update config for SageMaker
    config_path = f'/opt/ml/code/configs/rec/{args.config}'
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    updated_config = update_config_for_sagemaker(config_path, args)
    
    # Import PaddleOCR training
    try:
        import subprocess
        
        # Use PaddleOCR training script directly
        training_cmd = [
            'python', '/opt/ml/code/PaddleOCR/tools/train.py',
            '-c', updated_config
        ]
        
        logger.info(f"Starting PaddleOCR training with command: {' '.join(training_cmd)}")
        
        result = subprocess.run(training_cmd, cwd='/opt/ml/code', capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Training completed successfully!")
            logger.info(f"Training output: {result.stdout}")
        else:
            logger.error(f"Training failed with exit code: {result.returncode}")
            logger.error(f"Training stderr: {result.stderr}")
            logger.error(f"Training stdout: {result.stdout}")
            raise RuntimeError("Training failed")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise

if __name__ == '__main__':
    main()
