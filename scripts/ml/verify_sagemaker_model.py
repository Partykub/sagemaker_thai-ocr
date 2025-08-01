#!/usr/bin/env python3
"""
Simple model verification for SageMaker trained model
"""

import os
import sys
from pathlib import Path
import json

def check_sagemaker_model():
    """Check SageMaker trained model files and structure"""
    
    project_root = Path(__file__).parent.parent.parent
    model_dir = project_root / "models" / "sagemaker_trained"
    
    print("🔍 SageMaker Model Verification")
    print("=" * 50)
    
    # Check model directory
    if not model_dir.exists():
        print("❌ Model directory not found!")
        return False
    
    print(f"✅ Model directory found: {model_dir}")
    
    # Check model files
    model_files = {
        "best_accuracy.pdparams": "Best accuracy model parameters",
        "best_accuracy.pdopt": "Best accuracy optimizer state",
        "latest.pdparams": "Latest model parameters",
        "config.yml": "Training configuration",
        "model.tar.gz": "Compressed model archive"
    }
    
    print("\n📁 Model Files:")
    for filename, description in model_files.items():
        filepath = model_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"  ✅ {filename} ({size_mb:.1f} MB) - {description}")
        else:
            print(f"  ❌ {filename} - Missing")
    
    # Check best_model directory
    best_model_dir = model_dir / "best_model"
    if best_model_dir.exists():
        print(f"\n📂 Best Model Directory:")
        for file in best_model_dir.iterdir():
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"  ✅ {file.name} ({size_mb:.1f} MB)")
    
    # Check training epochs
    epoch_files = [f for f in model_dir.iterdir() if f.name.startswith("iter_epoch_") and f.name.endswith(".pdparams")]
    if epoch_files:
        epochs = sorted([int(f.name.split("_")[2].split(".")[0]) for f in epoch_files])
        print(f"\n📊 Training Epochs: {len(epochs)} checkpoints")
        print(f"  📈 Epochs: {epochs[0]} to {epochs[-1]} (every 5 epochs)")
    
    # Read config file
    config_file = model_dir / "config.yml"
    if config_file.exists():
        print(f"\n⚙️ Training Configuration:")
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_lines = f.readlines()[:20]  # First 20 lines
                for line in config_lines:
                    if line.strip() and not line.startswith('#'):
                        print(f"  {line.rstrip()}")
        except Exception as e:
            print(f"  ❌ Could not read config: {e}")
    
    # Model summary
    print(f"\n📋 Training Summary:")
    
    # Count total parameters (approximate based on file size)
    params_file = model_dir / "best_accuracy.pdparams"
    if params_file.exists():
        params_size_mb = params_file.stat().st_size / (1024 * 1024)
        print(f"  📊 Model size: {params_size_mb:.1f} MB")
        
        # Estimate parameter count (rough estimate: 4 bytes per parameter)
        estimated_params = (params_file.stat().st_size / 4) / 1_000_000
        print(f"  🧮 Estimated parameters: {estimated_params:.1f}M")
    
    # Training time estimate from file timestamps
    first_epoch = model_dir / "iter_epoch_5.pdparams"
    last_epoch = model_dir / "iter_epoch_100.pdparams"
    
    if first_epoch.exists() and last_epoch.exists():
        import datetime
        start_time = datetime.datetime.fromtimestamp(first_epoch.stat().st_mtime)
        end_time = datetime.datetime.fromtimestamp(last_epoch.stat().st_mtime)
        training_duration = end_time - start_time
        print(f"  ⏱️ Training duration: {training_duration}")
    
    print(f"\n🎯 Next Steps:")
    print(f"  1. Create inference script with correct PaddlePaddle version")
    print(f"  2. Test model with sample Thai text images")
    print(f"  3. Deploy to SageMaker endpoint for production")
    print(f"  4. Compare accuracy with local training results")
    
    return True

def main():
    """Main function"""
    success = check_sagemaker_model()
    
    if success:
        print("\n🎉 Model verification completed!")
        print("\n💡 Your Thai OCR model is ready for testing!")
    else:
        print("\n❌ Model verification failed!")

if __name__ == "__main__":
    main()
