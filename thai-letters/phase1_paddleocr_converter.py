#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 Phase 1: PaddleOCR Dataset Converter
แปลง Thai Dataset ที่มีอยู่ให้เป็น PaddleOCR Standard Format

สำหรับ dataset ที่สร้างแล้วใน thai-letters/
"""

import os
import sys
import json
import shutil
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class PaddleOCRDatasetConverter:
    """แปลง Thai Dataset เป็น PaddleOCR format"""
    
    def __init__(self, source_dataset_dir: str, train_val_split: float = 0.8):
        """
        Initialize converter
        
        Args:
            source_dataset_dir: โฟลเดอร์ dataset ต้นฉบับ
            train_val_split: อัตราส่วน train/validation
        """
        self.source_dir = Path(source_dataset_dir)
        self.train_val_split = train_val_split
        self.timestamp = datetime.now().strftime("%m%d_%H%M")
        
        # Output directory ตาม PaddleOCR standard
        self.output_dir = Path(f"train_data_thai_paddleocr_{self.timestamp}")
        
        # Statistics
        self.stats = {
            "total_images": 0,
            "train_images": 0,
            "val_images": 0,
            "characters": 0,
            "processed": 0,
            "errors": 0
        }
        
        print(f"🔥 PaddleOCR Dataset Converter")
        print(f"📁 Source: {self.source_dir}")
        print(f"📁 Output: {self.output_dir}")
    
    def validate_source_dataset(self) -> bool:
        """ตรวจสอบ dataset ต้นฉบับ"""
        print("🔍 Validating source dataset...")
        
        required_files = [
            "labels.txt",
            "dataset_details.json"
        ]
        
        # Check required files
        for file in required_files:
            file_path = self.source_dir / file
            if not file_path.exists():
                print(f"❌ Missing: {file}")
                return False
            print(f"✅ Found: {file}")
        
        # Check images directory
        images_dir = self.source_dir / "images"
        if not images_dir.exists():
            print("❌ Missing: images/ directory")
            return False
        
        # Count images
        image_count = len(list(images_dir.glob("*.jpg")))
        print(f"✅ Found {image_count:,} images")
        
        # Load and validate labels
        labels_file = self.source_dir / "labels.txt"
        with open(labels_file, 'r', encoding='utf-8') as f:
            labels = [line.strip() for line in f if line.strip()]
        
        print(f"✅ Found {len(labels):,} labels")
        
        if image_count != len(labels):
            print(f"⚠️ Warning: Image count ({image_count}) != Label count ({len(labels)})")
        
        self.stats["total_images"] = len(labels)
        
        return True
    
    def create_paddleocr_structure(self):
        """สร้างโครงสร้าง PaddleOCR standard"""
        print("📁 Creating PaddleOCR structure...")
        
        # Create directories
        structure_paths = [
            self.output_dir / "train_data" / "rec" / "thai_data" / "train",
            self.output_dir / "train_data" / "rec" / "thai_data" / "val"
        ]
        
        for path in structure_paths:
            path.mkdir(parents=True, exist_ok=True)
            print(f"  📁 Created: {path}")
        
        print("✅ PaddleOCR structure created")
    
    def load_and_split_data(self) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """โหลดและแบ่งข้อมูล train/validation"""
        print("📊 Loading and splitting data...")
        
        # Load labels
        labels_file = self.source_dir / "labels.txt"
        with open(labels_file, 'r', encoding='utf-8') as f:
            all_data = []
            for line in f:
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        img_name, char = parts
                        all_data.append((img_name, char))
        
        print(f"📋 Loaded {len(all_data):,} label pairs")
        
        # Shuffle for random split
        random.shuffle(all_data)
        
        # Split train/validation
        split_idx = int(len(all_data) * self.train_val_split)
        train_data = all_data[:split_idx]
        val_data = all_data[split_idx:]
        
        self.stats["train_images"] = len(train_data)
        self.stats["val_images"] = len(val_data)
        
        print(f"✅ Train: {len(train_data):,} samples ({len(train_data)/len(all_data)*100:.1f}%)")
        print(f"✅ Val: {len(val_data):,} samples ({len(val_data)/len(all_data)*100:.1f}%)")
        
        return train_data, val_data
    
    def copy_images_and_create_labels(self, train_data: List[Tuple[str, str]], 
                                    val_data: List[Tuple[str, str]]):
        """คัดลอกภาพและสร้างไฟล์ label"""
        print("🖼️ Copying images and creating labels...")
        
        source_images_dir = self.source_dir / "images"
        train_dir = self.output_dir / "train_data" / "rec" / "thai_data" / "train"
        val_dir = self.output_dir / "train_data" / "rec" / "thai_data" / "val"
        
        train_labels = []
        val_labels = []
        
        # Process training data
        print("  📋 Processing training data...")
        for i, (img_name, char) in enumerate(train_data):
            try:
                # Copy image
                src_path = source_images_dir / img_name
                dst_path = train_dir / img_name
                
                if src_path.exists():
                    shutil.copy2(src_path, dst_path)
                    train_labels.append(f"{img_name}\t{char}")
                    self.stats["processed"] += 1
                else:
                    print(f"  ⚠️ Missing image: {img_name}")
                    self.stats["errors"] += 1
                
                if (i + 1) % 1000 == 0:
                    print(f"    Processed {i+1:,}/{len(train_data):,} training images...")
            
            except Exception as e:
                print(f"  ❌ Error processing {img_name}: {e}")
                self.stats["errors"] += 1
        
        # Process validation data
        print("  📋 Processing validation data...")
        for i, (img_name, char) in enumerate(val_data):
            try:
                # Copy image
                src_path = source_images_dir / img_name
                dst_path = val_dir / img_name
                
                if src_path.exists():
                    shutil.copy2(src_path, dst_path)
                    val_labels.append(f"{img_name}\t{char}")
                    self.stats["processed"] += 1
                else:
                    print(f"  ⚠️ Missing image: {img_name}")
                    self.stats["errors"] += 1
                
                if (i + 1) % 1000 == 0:
                    print(f"    Processed {i+1:,}/{len(val_data):,} validation images...")
            
            except Exception as e:
                print(f"  ❌ Error processing {img_name}: {e}")
                self.stats["errors"] += 1
        
        # Save label files (PaddleOCR format)
        train_label_file = self.output_dir / "train_data" / "rec" / "rec_gt_train.txt"
        val_label_file = self.output_dir / "train_data" / "rec" / "rec_gt_val.txt"
        
        # Training labels
        with open(train_label_file, 'w', encoding='utf-8') as f:
            for label in train_labels:
                f.write(f"thai_data/train/{label}\n")  # Add path prefix
        
        # Validation labels  
        with open(val_label_file, 'w', encoding='utf-8') as f:
            for label in val_labels:
                f.write(f"thai_data/val/{label}\n")  # Add path prefix
        
        print(f"✅ Copied {self.stats['processed']:,} images")
        print(f"✅ Created {len(train_labels):,} training labels")
        print(f"✅ Created {len(val_labels):,} validation labels")
    
    def copy_dictionary_and_corpus(self):
        """คัดลอกไฟล์ dictionary และ corpus"""
        print("📚 Copying dictionary and corpus...")
        
        # Dictionary
        src_dict = Path(__file__).parent / "th_dict.txt"
        dst_dict = self.output_dir / "train_data" / "th_dict.txt"
        
        if src_dict.exists():
            shutil.copy2(src_dict, dst_dict)
            print(f"✅ Dictionary copied: {dst_dict}")
            
            # Count characters
            with open(src_dict, 'r', encoding='utf-8') as f:
                chars = [line.strip() for line in f if line.strip()]
            self.stats["characters"] = len(chars)
            print(f"📊 Dictionary contains {len(chars)} characters")
        else:
            print("⚠️ th_dict.txt not found in thai-letters/")
        
        # Corpus
        src_corpus = Path(__file__).parent / "thai_corpus.txt"
        dst_corpus = self.output_dir / "train_data" / "th_corpus.txt"
        
        if src_corpus.exists():
            shutil.copy2(src_corpus, dst_corpus)
            print(f"✅ Corpus copied: {dst_corpus}")
            
            # Count words
            with open(src_corpus, 'r', encoding='utf-8') as f:
                words = [line.strip() for line in f if line.strip()]
            print(f"📖 Corpus contains {len(words):,} words")
        else:
            print("⚠️ thai_corpus.txt not found in thai-letters/")
    
    def create_config_files(self):
        """สร้างไฟล์ config สำหรับ PaddleOCR"""
        print("⚙️ Creating PaddleOCR config files...")
        
        # Training config
        config = {
            "Global": {
                "use_gpu": True,
                "epoch_num": 500,
                "log_smooth_window": 20,
                "print_batch_step": 10,
                "save_model_dir": "./output/rec_thai_svtr_tiny/",
                "save_epoch_step": 3,
                "eval_batch_step": [0, 2000],
                "cal_metric_during_train": True,
                "pretrained_model": None,
                "checkpoints": None,
                "save_inference_dir": None,
                "use_visualdl": False,
                "infer_img": None,
                "character_dict_path": "./train_data/th_dict.txt",
                "character_type": "thai",
                "max_text_length": 25,
                "infer_mode": False,
                "use_space_char": False,
                "distributed": True,
                "save_res_path": "./output/rec/predicts_svtr_tiny.txt"
            },
            "Optimizer": {
                "name": "Adam",
                "beta1": 0.9,
                "beta2": 0.999,
                "lr": {
                    "name": "Cosine",
                    "learning_rate": 0.001,
                    "warmup_epoch": 5
                },
                "regularizer": {
                    "name": "L2",
                    "factor": 3e-05
                }
            },
            "Architecture": {
                "model_type": "rec",
                "algorithm": "SVTR_LCNet",
                "Transform": None,
                "Backbone": {
                    "name": "SVTRNet",
                    "img_size": [64, 256],
                    "out_char_num": 25,
                    "out_channels": 192,
                    "patch_merging": "Conv",
                    "embed_dim": [64, 128, 256],
                    "depth": [3, 6, 3],
                    "num_heads": [2, 4, 8],
                    "mixer": ["Local"] * 6 + ["Global"] * 6,
                    "local_mixer": [[7, 11], [7, 11], [7, 11]],
                    "last_stage": True,
                    "prenorm": False
                },
                "Head": {
                    "name": "CTCHead",
                    "fc_decay": 0.00001
                }
            },
            "Loss": {
                "name": "CTCLoss"
            },
            "PostProcess": {
                "name": "CTCLabelDecode"
            },
            "Metric": {
                "name": "RecMetric",
                "main_indicator": "acc"
            },
            "Train": {
                "dataset": {
                    "name": "SimpleDataSet",
                    "data_dir": "./train_data/rec/thai_data/",
                    "ext_op_transform_idx": 1,
                    "label_file_list": ["./train_data/rec/rec_gt_train.txt"],
                    "transforms": [
                        {"DecodeImage": {"img_mode": "BGR", "channel_first": False}},
                        {"RecConAug": {"prob": 0.5, "ext_data_num": 2, "image_shape": [48, 320, 3], "max_text_length": 25}},
                        {"RecAug": {}},
                        {"MultiLabelEncode": {}},
                        {"RecResizeImg": {"image_shape": [3, 64, 256]}},
                        {"KeepKeys": {"keep_keys": ["image", "label", "length", "valid_ratio"]}}
                    ]
                },
                "loader": {
                    "shuffle": True,
                    "batch_size_per_card": 128,
                    "drop_last": True,
                    "num_workers": 4
                }
            },
            "Eval": {
                "dataset": {
                    "name": "SimpleDataSet", 
                    "data_dir": "./train_data/rec/thai_data/",
                    "label_file_list": ["./train_data/rec/rec_gt_val.txt"],
                    "transforms": [
                        {"DecodeImage": {"img_mode": "BGR", "channel_first": False}},
                        {"MultiLabelEncode": {}},
                        {"RecResizeImg": {"image_shape": [3, 64, 256]}},
                        {"KeepKeys": {"keep_keys": ["image", "label", "length", "valid_ratio"]}}
                    ]
                },
                "loader": {
                    "shuffle": False,
                    "drop_last": False,
                    "batch_size_per_card": 128,
                    "num_workers": 4
                }
            }
        }
        
        # Save config file
        config_file = self.output_dir / "thai_svtr_tiny_config.yml"
        
        # Convert to YAML-like format (simple approach)
        yaml_content = self._dict_to_yaml(config, 0)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        print(f"✅ Config saved: {config_file}")
    
    def _dict_to_yaml(self, data, indent_level):
        """Convert dict to YAML format (simple implementation)"""
        yaml_str = ""
        indent = "  " * indent_level
        
        for key, value in data.items():
            if isinstance(value, dict):
                yaml_str += f"{indent}{key}:\n"
                yaml_str += self._dict_to_yaml(value, indent_level + 1)
            elif isinstance(value, list):
                yaml_str += f"{indent}{key}:\n"
                for item in value:
                    if isinstance(item, dict):
                        yaml_str += f"{indent}  -\n"
                        yaml_str += self._dict_to_yaml(item, indent_level + 2)
                    else:
                        yaml_str += f"{indent}  - {item}\n"
            else:
                if isinstance(value, str):
                    yaml_str += f"{indent}{key}: {value}\n"
                else:
                    yaml_str += f"{indent}{key}: {value}\n"
        
        return yaml_str
    
    def generate_report(self):
        """สร้างรายงาน"""
        print("📋 Generating conversion report...")
        
        report_file = self.output_dir / "PHASE1_PADDLEOCR_CONVERSION_REPORT.md"
        
        success_rate = ((self.stats["processed"] / self.stats["total_images"]) * 100) if self.stats["total_images"] > 0 else 0
        
        report_content = f"""# 🔥 Phase 1: PaddleOCR Dataset Conversion Report

**Generated on:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Source Dataset:** {self.source_dir.name}  
**Conversion Status:** ✅ COMPLETED

## 📊 Conversion Statistics

- **Total Source Images:** {self.stats['total_images']:,}
- **Successfully Processed:** {self.stats['processed']:,}
- **Training Images:** {self.stats['train_images']:,} ({self.stats['train_images']/self.stats['total_images']*100:.1f}%)
- **Validation Images:** {self.stats['val_images']:,} ({self.stats['val_images']/self.stats['total_images']*100:.1f}%)
- **Thai Characters:** {self.stats['characters']:,}
- **Success Rate:** {success_rate:.2f}%
- **Errors:** {self.stats['errors']}

## 📁 PaddleOCR Dataset Structure

```
{self.output_dir.name}/
├── train_data/
│   ├── rec/
│   │   ├── thai_data/
│   │   │   ├── train/           # {self.stats['train_images']:,} training images
│   │   │   └── val/             # {self.stats['val_images']:,} validation images
│   │   ├── rec_gt_train.txt     # Training labels (PaddleOCR format)
│   │   └── rec_gt_val.txt       # Validation labels (PaddleOCR format)
│   ├── th_dict.txt              # Thai character dictionary ({self.stats['characters']} chars)
│   └── th_corpus.txt            # Thai text corpus
├── thai_svtr_tiny_config.yml    # PaddleOCR training configuration
└── PHASE1_PADDLEOCR_CONVERSION_REPORT.md
```

## 🚀 Ready for PaddleOCR Training

### Step 1: Install PaddleOCR
```bash
pip install paddlepaddle-gpu paddleocr
```

### Step 2: Start Training
```bash
# Change to dataset directory
cd {self.output_dir.name}

# Start training with custom config
python -m paddle.distributed.launch \\
    --gpus="0" \\
    tools/train.py \\
    -c thai_svtr_tiny_config.yml
```

### Step 3: Monitor Training
```bash
# Check training progress
tensorboard --logdir=./output/rec_thai_svtr_tiny/
```

## 📋 Label Format Validation

### Training Labels (`rec_gt_train.txt`):
- **Format:** `thai_data/train/image_name.jpg\\tcharacter`
- **Example:** `thai_data/train/000_00.jpg\\tก`
- **Count:** {self.stats['train_images']:,} entries

### Validation Labels (`rec_gt_val.txt`):
- **Format:** `thai_data/val/image_name.jpg\\tcharacter` 
- **Example:** `thai_data/val/001_00.jpg\\tข`
- **Count:** {self.stats['val_images']:,} entries

## ⚙️ Training Configuration

- **Model:** SVTR_LCNet (State-of-the-art OCR model)
- **Image Size:** 64x256 pixels
- **Batch Size:** 128
- **Learning Rate:** 0.001 (Cosine decay)
- **Epochs:** 500
- **GPU:** Required (use_gpu: true)

## 🎯 Expected Results

- **Training Time:** ~2-4 hours on RTX 5090
- **Accuracy Target:** 90-95% on Thai characters
- **Model Size:** ~10-20MB after optimization
- **Inference Speed:** ~100-200 images/second

## 🔧 Troubleshooting

### Common Issues:
1. **GPU Memory:** Reduce batch_size if OOM error
2. **Character Encoding:** Ensure UTF-8 encoding for all text files
3. **Path Issues:** Use absolute paths if relative paths fail

### Performance Tips:
1. **Data Augmentation:** Already enabled in config
2. **Learning Rate:** Auto-adjusted with warmup
3. **Early Stopping:** Monitor validation accuracy

---

**✅ Dataset converted successfully and ready for PaddleOCR training!**
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📋 Report saved: {report_file}")
    
    def convert_dataset(self):
        """แปลง dataset หลัก"""
        print("🚀 Starting PaddleOCR dataset conversion...")
        print("=" * 60)
        
        try:
            # Step 1: Validate source
            if not self.validate_source_dataset():
                print("❌ Source dataset validation failed")
                return False
            
            # Step 2: Create structure
            self.create_paddleocr_structure()
            
            # Step 3: Load and split data
            train_data, val_data = self.load_and_split_data()
            
            # Step 4: Copy images and create labels
            self.copy_images_and_create_labels(train_data, val_data)
            
            # Step 5: Copy dictionary and corpus
            self.copy_dictionary_and_corpus()
            
            # Step 6: Create config files
            self.create_config_files()
            
            # Step 7: Generate report
            self.generate_report()
            
            print("=" * 60)
            print("✅ PaddleOCR Dataset Conversion Complete!")
            print(f"📁 Output: {self.output_dir}")
            print(f"🎯 Ready for PaddleOCR training")
            
            return True
            
        except Exception as e:
            print(f"❌ Conversion failed: {e}")
            return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🔥 Convert Thai Dataset to PaddleOCR format")
    parser.add_argument("source_dir", type=str, 
                       help="Source dataset directory")
    parser.add_argument("--split", type=float, default=0.8,
                       help="Train/validation split ratio (default: 0.8)")
    
    args = parser.parse_args()
    
    print("🔥 PaddleOCR Dataset Converter - Phase 1")
    print("🎯 Converting Thai dataset to PaddleOCR standard format")
    print("=" * 60)
    
    # Check source directory
    if not Path(args.source_dir).exists():
        print(f"❌ Source directory not found: {args.source_dir}")
        sys.exit(1)
    
    # Initialize converter
    converter = PaddleOCRDatasetConverter(
        source_dataset_dir=args.source_dir,
        train_val_split=args.split
    )
    
    # Convert dataset
    success = converter.convert_dataset()
    
    if success:
        print("🎉 Conversion completed successfully!")
        print("📁 Your PaddleOCR dataset is ready for training")
        sys.exit(0)
    else:
        print("❌ Conversion failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
