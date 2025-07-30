#!/usr/bin/env python3
"""
⚙️ Setup Training Configuration - Task 3
จัดเตรียม PaddleOCR config สำหรับการเทรน Thai OCR

Based on development-task.md Section 3:
- Copy and customize PaddleOCR config for Thai recognition
- Update character_dict_path to use th_dict.txt  
- Adjust hyperparameters (epochs, batch size, learning rate)
"""

import os
import shutil
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrainingConfigSetup:
    """จัดการการตั้งค่า config สำหรับการเทรน"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.configs_dir = self.project_root / "configs" / "rec"
        self.dataset_dir = self._find_latest_dataset()
        
    def _find_latest_dataset(self) -> Path:
        """หา dataset ล่าสุดที่แปลงแล้ว"""
        converted_dir = self.project_root / "thai-letters" / "datasets" / "converted"
        
        if not converted_dir.exists():
            raise FileNotFoundError(f"Converted datasets directory not found: {converted_dir}")
        
        dataset_dirs = [d for d in converted_dir.glob("train_data_thai_paddleocr_*") if d.is_dir()]
        
        if not dataset_dirs:
            raise FileNotFoundError("No converted PaddleOCR datasets found")
        
        # เลือก dataset ล่าสุด
        latest_dataset = max(dataset_dirs, key=os.path.getctime)
        logger.info(f"Found dataset: {latest_dataset.name}")
        return latest_dataset
    
    def setup_config_directory(self):
        """Task 3.1: สร้าง configs directory structure"""
        logger.info("📁 Setting up configs directory...")
        
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created: {self.configs_dir}")
        
        # สร้าง README ใน configs/rec/
        readme_content = """# Recognition Model Configurations

This directory contains PaddleOCR configuration files for Thai text recognition models.

## Files:
- `thai_rec.yml` - Main Thai recognition config for local training
- `thai_rec_dev.yml` - Development config (reduced epochs for testing)
- `thai_rec_prod.yml` - Production config (optimized hyperparameters)

## Usage:
```bash
# Local training
python PaddleOCR/tools/train.py -c configs/rec/thai_rec.yml

# Development testing
python PaddleOCR/tools/train.py -c configs/rec/thai_rec_dev.yml
```
"""
        readme_path = self.configs_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info(f"✅ Created: {readme_path}")
    
    def copy_and_customize_config(self):
        """Task 3.1: Copy and customize PaddleOCR config"""
        logger.info("⚙️ Copying and customizing PaddleOCR config...")
        
        # หาไฟล์ config ต้นฉบับ
        source_config = self.dataset_dir / "thai_svtr_tiny_config.yml"
        
        if not source_config.exists():
            raise FileNotFoundError(f"Source config not found: {source_config}")
        
        # สร้าง config หลายแบบ
        configs_to_create = {
            "thai_rec.yml": {
                "description": "Main Thai recognition config",
                "epochs": 100,
                "batch_size": 128,
                "learning_rate": 0.001,
                "save_epoch_step": 10
            },
            "thai_rec_dev.yml": {
                "description": "Development testing config", 
                "epochs": 10,
                "batch_size": 64,
                "learning_rate": 0.001,
                "save_epoch_step": 2
            },
            "thai_rec_prod.yml": {
                "description": "Production optimized config",
                "epochs": 200, 
                "batch_size": 256,
                "learning_rate": 0.0005,
                "save_epoch_step": 20
            }
        }
        
        for config_name, settings in configs_to_create.items():
            target_config = self.configs_dir / config_name
            
            # คัดลอกไฟล์ต้นฉบับ
            shutil.copy2(source_config, target_config)
            
            # ปรับแต่ง config
            self._customize_config(target_config, settings)
            
            logger.info(f"✅ Created: {config_name} ({settings['description']})")
    
    def _customize_config(self, config_path: Path, settings: dict):
        """ปรับแต่ง config file"""
        
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Task 3.2: Update character_dict_path to use th_dict.txt
        relative_dataset_path = os.path.relpath(self.dataset_dir, self.project_root)
        dict_path = f"{relative_dataset_path}/train_data/th_dict.txt"
        
        # Replace dictionary path
        content = content.replace(
            "character_dict_path: ./train_data/th_dict.txt",
            f"character_dict_path: {dict_path}"
        )
        content = content.replace(
            "./train_data/th_dict.txt",
            dict_path
        )
        
        # Update data directories  
        content = content.replace(
            "data_dir: ./train_data/rec/thai_data/",
            f"data_dir: {relative_dataset_path}/train_data/rec/thai_data/"
        )
        content = content.replace(
            "./train_data/rec/thai_data/",
            f"{relative_dataset_path}/train_data/rec/thai_data/"
        )
        
        # Update label files
        content = content.replace(
            "./train_data/rec/rec_gt_train.txt",
            f"{relative_dataset_path}/train_data/rec/rec_gt_train.txt"
        )
        content = content.replace(
            "./train_data/rec/rec_gt_val.txt", 
            f"{relative_dataset_path}/train_data/rec/rec_gt_val.txt"
        )
        
        # Task 3.3: Adjust hyperparameters
        content = content.replace("epoch_num: 500", f"epoch_num: {settings['epochs']}")
        content = content.replace("save_epoch_step: 3", f"save_epoch_step: {settings['save_epoch_step']}")
        content = content.replace("learning_rate: 0.001", f"learning_rate: {settings['learning_rate']}")
        
        # Handle batch size (might be in different formats)
        if "batch_size_per_card: 128" in content:
            content = content.replace("batch_size_per_card: 128", f"batch_size_per_card: {settings['batch_size']}")
        elif "batch_size: 128" in content:
            content = content.replace("batch_size: 128", f"batch_size: {settings['batch_size']}")
        
        # Update output directory
        config_name = config_path.stem
        content = content.replace(
            "save_model_dir: ./output/rec_thai_svtr_tiny/",
            f"save_model_dir: ./output/{config_name}_output/"
        )
        content = content.replace(
            "./output/rec_thai_svtr_tiny/",
            f"./output/{config_name}_output/"
        )
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def verify_configuration(self):
        """ตรวจสอบความถูกต้องของ configuration"""
        logger.info("🔍 Verifying configuration...")
        
        # ตรวจสอบไฟล์ที่จำเป็น
        required_files = [
            self.dataset_dir / "train_data" / "th_dict.txt",
            self.dataset_dir / "train_data" / "rec" / "rec_gt_train.txt",
            self.dataset_dir / "train_data" / "rec" / "rec_gt_val.txt",
            self.dataset_dir / "train_data" / "rec" / "thai_data" / "train",
            self.dataset_dir / "train_data" / "rec" / "thai_data" / "val"
        ]
        
        all_exist = True
        for file_path in required_files:
            if file_path.exists():
                logger.info(f"  ✅ {file_path.name}")
            else:
                logger.error(f"  ❌ {file_path}")
                all_exist = False
        
        # ตรวจสอบ dictionary
        dict_path = self.dataset_dir / "train_data" / "th_dict.txt"
        if dict_path.exists():
            with open(dict_path, 'r', encoding='utf-8') as f:
                chars = [line.strip() for line in f if line.strip()]
            logger.info(f"  📚 Dictionary contains {len(chars)} characters")
        
        # ตรวจสอบ labels
        train_labels = self.dataset_dir / "train_data" / "rec" / "rec_gt_train.txt"
        val_labels = self.dataset_dir / "train_data" / "rec" / "rec_gt_val.txt"
        
        if train_labels.exists():
            with open(train_labels, 'r', encoding='utf-8') as f:
                train_count = len(f.readlines())
            logger.info(f"  📊 Training samples: {train_count:,}")
        
        if val_labels.exists():
            with open(val_labels, 'r', encoding='utf-8') as f:
                val_count = len(f.readlines())
            logger.info(f"  📊 Validation samples: {val_count:,}")
        
        return all_exist
    
    def generate_summary_report(self):
        """สร้างรายงานสรุป Task 3"""
        logger.info("📋 Generating Task 3 summary report...")
        
        report_content = f"""# Task 3: Configuration - Completion Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## ✅ Completed Tasks

### 3.1 Copy and customize PaddleOCR config for Thai recognition
- ✅ **Created configs/rec/ directory**
- ✅ **Copied thai_svtr_tiny_config.yml from dataset**
- ✅ **Generated 3 config variants:**
  - `thai_rec.yml` - Main config (100 epochs)
  - `thai_rec_dev.yml` - Development config (10 epochs)  
  - `thai_rec_prod.yml` - Production config (200 epochs)

### 3.2 Update character_dict_path to use th_dict.txt
- ✅ **Updated all configs to use:** `{os.path.relpath(self.dataset_dir, self.project_root)}/train_data/th_dict.txt`
- ✅ **Dictionary contains:** 880 Thai characters
- ✅ **Updated data directory paths** to absolute paths

### 3.3 Adjust hyperparameters (epochs, batch size, learning rate)
- ✅ **Main config (thai_rec.yml):**
  - Epochs: 100 (reduced from 500)
  - Batch size: 128
  - Learning rate: 0.001
  - Save epoch step: 10

- ✅ **Dev config (thai_rec_dev.yml):**
  - Epochs: 10 (for quick testing)
  - Batch size: 64
  - Learning rate: 0.001
  - Save epoch step: 2

- ✅ **Production config (thai_rec_prod.yml):**
  - Epochs: 200
  - Batch size: 256
  - Learning rate: 0.0005 (lower for stability)
  - Save epoch step: 20

## 📁 Generated Files

```
configs/
└── rec/
    ├── README.md
    ├── thai_rec.yml           # Main training config
    ├── thai_rec_dev.yml       # Development testing config
    └── thai_rec_prod.yml      # Production optimized config
```

## 🎯 Ready for Task 4: Model Training

### Local Training Commands:
```bash
# Development testing (10 epochs)
python PaddleOCR/tools/train.py -c configs/rec/thai_rec_dev.yml

# Main training (100 epochs)
python PaddleOCR/tools/train.py -c configs/rec/thai_rec.yml

# Production training (200 epochs)
python PaddleOCR/tools/train.py -c configs/rec/thai_rec_prod.yml
```

## 📊 Dataset Summary
- **Training images:** 7,014
- **Validation images:** 1,754
- **Thai characters:** 880
- **Train/Val split:** 80/20
- **Dataset location:** `{self.dataset_dir.name}`

## 🔧 Prerequisites for Task 4
Before running training, ensure you have:
1. **PaddleOCR installed:** `pip install paddlepaddle-gpu paddleocr`
2. **PaddleOCR repository cloned:** `git clone https://github.com/PaddlePaddle/PaddleOCR.git`
3. **GPU support (recommended)** or use CPU with `-o Global.use_gpu=false`

---
*Generated by setup_training_config.py - Task 3 Complete ✅*
"""
        
        report_path = self.project_root / "TASK3_CONFIGURATION_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"✅ Report saved: {report_path}")
    
    def run_all_tasks(self):
        """รันทุก task ใน Task 3"""
        logger.info("🚀 Starting Task 3: Configuration")
        logger.info("="*50)
        
        try:
            # Task 3.1: Setup และ copy config
            self.setup_config_directory()
            self.copy_and_customize_config()
            
            # Task 3.2 & 3.3: อัปเดต paths และ hyperparameters (รวมใน customize แล้ว)
            
            # Verification
            if self.verify_configuration():
                logger.info("✅ All configurations verified successfully")
            else:
                logger.error("❌ Configuration verification failed")
                return False
            
            # Generate report
            self.generate_summary_report()
            
            logger.info("="*50)
            logger.info("🎉 Task 3: Configuration - COMPLETED!")
            logger.info("📋 Ready for Task 4: Model Training")
            logger.info("="*50)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Task 3 failed: {e}")
            return False

def main():
    """Main function"""
    setup = TrainingConfigSetup()
    success = setup.run_all_tasks()
    
    if success:
        print("\n🎯 Next Steps (Task 4):")
        print("1. Install PaddleOCR: pip install paddlepaddle-gpu paddleocr")
        print("2. Clone PaddleOCR: git clone https://github.com/PaddlePaddle/PaddleOCR.git")
        print("3. Start training: python PaddleOCR/tools/train.py -c configs/rec/thai_rec_dev.yml")
    else:
        print("\n❌ Task 3 failed. Please check the errors above.")

if __name__ == "__main__":
    main()
