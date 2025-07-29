#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Quick Phase 1: Thai Dataset to PaddleOCR Converter
One-click conversion สำหรับ dataset ที่มีอยู่

ใช้งาน: python quick_phase1_converter.py
"""

import os
import sys
from pathlib import Path
from phase1_paddleocr_converter import PaddleOCRDatasetConverter

def find_existing_datasets():
    """หา dataset ที่มีอยู่ใน thai-letters/"""
    current_dir = Path(__file__).parent
    datasets = []
    
    for item in current_dir.iterdir():
        if item.is_dir():
            # Check multiple patterns for dataset directories
            is_dataset = (
                item.name.startswith("thai_dataset") or
                "samples" in item.name.lower() or
                "dataset" in item.name.lower()
            )
            
            if is_dataset:
                # Check if it has required files
                if (item / "labels.txt").exists() and (item / "images").exists():
                    datasets.append(item)
                # Also check if images directory exists inside
                elif (item / "labels.txt").exists():
                    # Count jpg files in any subdirectory
                    jpg_files = list(item.rglob("*.jpg"))
                    if jpg_files:
                        datasets.append(item)
    
    return datasets

def show_menu(datasets):
    """แสดงเมนูเลือก dataset"""
    print("🔥 Quick Phase 1: Thai Dataset to PaddleOCR Converter")
    print("=" * 60)
    
    if not datasets:
        print("❌ No existing Thai datasets found in thai-letters/")
        print("💡 Please generate a dataset first using:")
        print("   python thai_dataset_quick.py 10")
        return None
    
    print("📁 Found Thai datasets:")
    for i, dataset in enumerate(datasets, 1):
        # Get dataset info
        labels_file = dataset / "labels.txt"
        if labels_file.exists():
            with open(labels_file, 'r', encoding='utf-8') as f:
                label_count = len(f.readlines())
        else:
            label_count = 0
        
        images_dir = dataset / "images"
        if images_dir.exists():
            image_count = len(list(images_dir.glob("*.jpg")))
        else:
            image_count = 0
        
        print(f"  {i}. {dataset.name}")
        print(f"     📊 {image_count:,} images, {label_count:,} labels")
    
    print()
    while True:
        try:
            choice = input(f"Select dataset (1-{len(datasets)}) or 'q' to quit: ")
            if choice.lower() == 'q':
                return None
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(datasets):
                return datasets[choice_idx]
            else:
                print(f"❌ Please enter a number between 1 and {len(datasets)}")
        
        except ValueError:
            print("❌ Please enter a valid number or 'q'")

def get_split_ratio():
    """รับอัตราส่วน train/validation"""
    print("\n📊 Train/Validation Split Configuration:")
    print("  Default: 80% train, 20% validation")
    
    while True:
        choice = input("Use default split (80/20)? [Y/n]: ").strip().lower()
        
        if choice in ['', 'y', 'yes']:
            return 0.8
        elif choice in ['n', 'no']:
            while True:
                try:
                    split = float(input("Enter train ratio (0.1-0.9): "))
                    if 0.1 <= split <= 0.9:
                        return split
                    else:
                        print("❌ Please enter a value between 0.1 and 0.9")
                except ValueError:
                    print("❌ Please enter a valid number")
        else:
            print("❌ Please enter 'y' or 'n'")

def main():
    """Main function"""
    print("🔍 Scanning for existing Thai datasets...")
    
    # Find existing datasets
    datasets = find_existing_datasets()
    
    # Show menu and get selection
    selected_dataset = show_menu(datasets)
    if not selected_dataset:
        print("👋 Goodbye!")
        return
    
    # Get train/validation split
    split_ratio = get_split_ratio()
    
    print(f"\n🎯 Converting dataset: {selected_dataset.name}")
    print(f"📊 Train/Val split: {split_ratio*100:.0f}% / {(1-split_ratio)*100:.0f}%")
    print("-" * 40)
    
    # Initialize and run converter
    converter = PaddleOCRDatasetConverter(
        source_dataset_dir=str(selected_dataset),
        train_val_split=split_ratio
    )
    
    success = converter.convert_dataset()
    
    if success:
        print("\n🎉 SUCCESS! Your dataset is ready for PaddleOCR training")
        print(f"📁 Location: {converter.output_dir}")
        print("\n🚀 Next Steps:")
        print("1. Install PaddleOCR: pip install paddlepaddle-gpu paddleocr")
        print(f"2. Go to directory: cd {converter.output_dir}")
        print("3. Start training: python -m paddle.distributed.launch --gpus=\"0\" tools/train.py -c thai_svtr_tiny_config.yml")
        print("\n📋 Check the conversion report for detailed instructions!")
    else:
        print("\n❌ Conversion failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
