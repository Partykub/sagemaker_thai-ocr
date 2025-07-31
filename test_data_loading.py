#!/usr/bin/env python3
"""
Test data loading with corrected paths
"""

import os
import sys
sys.path.append('PaddleOCR')

# Test simple file access
data_dir = "/home/partykub/workspace/Documents/sagemaker_thai-ocr/thai-letters/datasets/converted/train_data_thai_paddleocr_0730_1648/train_data/rec/"
label_file = "/home/partykub/workspace/Documents/sagemaker_thai-ocr/thai-letters/datasets/converted/train_data_thai_paddleocr_0730_1648/train_data/rec/rec_gt_train.txt"

print("=== Testing Data Loading ===")
print(f"Data dir exists: {os.path.exists(data_dir)}")
print(f"Label file exists: {os.path.exists(label_file)}")

# Read first few lines of label file
if os.path.exists(label_file):
    with open(label_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:5]
    print(f"\nFirst 5 label lines:")
    for i, line in enumerate(lines):
        parts = line.strip().split('\t')
        if len(parts) >= 2:
            img_path, label = parts[0], parts[1]
            full_img_path = os.path.join(data_dir, img_path)
            exists = os.path.exists(full_img_path)
            print(f"  {i+1}. {img_path} -> {label} (exists: {exists})")
            if not exists:
                print(f"     Full path: {full_img_path}")
        else:
            print(f"  {i+1}. Invalid line: {line.strip()}")

# Test reading images
print("\n=== Testing Image Loading ===")
try:
    import cv2
    import numpy as np
    
    # Test first image
    if os.path.exists(label_file):
        with open(label_file, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        
        parts = first_line.split('\t')
        if len(parts) >= 2:
            img_path = parts[0]
            full_img_path = os.path.join(data_dir, img_path)
            
            if os.path.exists(full_img_path):
                img = cv2.imread(full_img_path)
                if img is not None:
                    print(f"✅ Successfully loaded image: {img_path}")
                    print(f"   Shape: {img.shape}")
                else:
                    print(f"❌ Failed to load image (cv2.imread returned None): {img_path}")
            else:
                print(f"❌ Image file not found: {full_img_path}")
        else:
            print("❌ Invalid label format")
            
except ImportError:
    print("cv2 not available for image testing")
except Exception as e:
    print(f"❌ Error during image testing: {e}")

print("\n=== Path Analysis ===")
# Check the actual directory structure
thai_data_dir = os.path.join(data_dir, "thai_data")
print(f"thai_data directory: {thai_data_dir}")
print(f"thai_data exists: {os.path.exists(thai_data_dir)}")

if os.path.exists(thai_data_dir):
    subdirs = [d for d in os.listdir(thai_data_dir) if os.path.isdir(os.path.join(thai_data_dir, d))]
    print(f"Subdirectories in thai_data: {subdirs}")
    
    train_dir = os.path.join(thai_data_dir, "train")
    if os.path.exists(train_dir):
        train_files = os.listdir(train_dir)
        print(f"Files in train directory: {len(train_files)} files")
        print(f"First 5 files: {train_files[:5]}")
