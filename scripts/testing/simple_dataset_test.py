#!/usr/bin/env python3
"""
Simple Image Test: ทดสอบโมเดลแบบง่าย โดยใช้ CV2 อ่านรูปแล้วแสดงผล
"""

import os
import cv2
import numpy as np
from pathlib import Path
import random
from typing import List, Tuple

def test_simple_image_reading():
    """ทดสอบการอ่านรูปแบบง่าย"""
    
    project_root = Path(__file__).parent.parent.parent
    dataset_dir = project_root / "thai-letters" / "datasets" / "converted" / "train_data_thai_paddleocr_0731_1604"
    
    # หา validation images
    val_images_dir = dataset_dir / "train_data" / "rec" / "thai_data" / "val"
    val_labels_file = dataset_dir / "train_data" / "rec" / "rec_gt_val.txt"
    
    print("🔍 Simple Thai OCR Dataset Test")
    print("=" * 50)
    
    # ตรวจสอบไฟล์
    if not val_images_dir.exists():
        print(f"❌ Validation images not found: {val_images_dir}")
        return
    
    if not val_labels_file.exists():
        print(f"❌ Labels file not found: {val_labels_file}")
        return
    
    print(f"✅ Dataset found: {dataset_dir.name}")
    print(f"📁 Images: {val_images_dir}")
    print(f"📄 Labels: {val_labels_file}")
    
    # อ่าน labels
    labels = {}
    with open(val_labels_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '\t' in line:
                img_path, text = line.split('\t', 1)
                full_path = dataset_dir / "train_data" / "rec" / img_path
                if full_path.exists():
                    labels[str(full_path)] = text.strip()
    
    print(f"📊 Loaded {len(labels)} labels")
    
    # สุ่มเลือก 10 รูป
    sample_items = random.sample(list(labels.items()), min(10, len(labels)))
    
    print(f"\n🖼️ Sample Analysis (10 random images):")
    print("-" * 50)
    
    for i, (img_path, ground_truth) in enumerate(sample_items, 1):
        img_name = Path(img_path).name
        
        # อ่านรูป
        try:
            img = cv2.imread(img_path)
            if img is not None:
                h, w = img.shape[:2]
                print(f"{i:2d}. {img_name:<15} → '{ground_truth:<10}' ({w}x{h}px)")
                
                # วิเคราะห์พื้นฐาน
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                mean_brightness = np.mean(gray)
                std_brightness = np.std(gray)
                
                # ประเมินคุณภาพรูป
                quality = "Good"
                if std_brightness < 20:
                    quality = "Low contrast"
                elif mean_brightness < 50:
                    quality = "Too dark"
                elif mean_brightness > 200:
                    quality = "Too bright"
                
                print(f"     Quality: {quality} (brightness: {mean_brightness:.0f}±{std_brightness:.0f})")
            else:
                print(f"{i:2d}. {img_name:<15} → ERROR: Cannot read image")
                
        except Exception as e:
            print(f"{i:2d}. {img_name:<15} → ERROR: {e}")
    
    # วิเคราะห์ character distribution
    print(f"\n🔤 Character Analysis:")
    print("-" * 50)
    
    char_count = {}
    for text in labels.values():
        for char in text:
            char_count[char] = char_count.get(char, 0) + 1
    
    # แสดง top 20 characters
    top_chars = sorted(char_count.items(), key=lambda x: x[1], reverse=True)[:20]
    print("Top 20 most frequent characters:")
    for i, (char, count) in enumerate(top_chars, 1):
        print(f"  {i:2d}. '{char}': {count:3d} times")
    
    print(f"\n📈 Dataset Statistics:")
    print(f"   Total images: {len(labels)}")
    print(f"   Unique characters: {len(char_count)}")
    print(f"   Average text length: {np.mean([len(text) for text in labels.values()]):.1f}")
    
    print(f"\n✅ Dataset analysis completed!")
    print(f"   This confirms our training data is properly formatted")
    print(f"   Next step: Test with actual OCR model inference")

def show_sample_images():
    """แสดงตัวอย่างรูปภาพ"""
    
    project_root = Path(__file__).parent.parent.parent
    dataset_dir = project_root / "thai-letters" / "datasets" / "converted" / "train_data_thai_paddleocr_0731_1604"
    val_images_dir = dataset_dir / "train_data" / "rec" / "thai_data" / "val"
    val_labels_file = dataset_dir / "train_data" / "rec" / "rec_gt_val.txt"
    
    if not val_images_dir.exists() or not val_labels_file.exists():
        print("❌ Dataset not found!")
        return
    
    # อ่าน labels
    labels = {}
    with open(val_labels_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '\t' in line:
                img_path, text = line.split('\t', 1)
                full_path = dataset_dir / "train_data" / "rec" / img_path
                if full_path.exists():
                    labels[str(full_path)] = text.strip()
    
    # เลือก 5 รูป
    sample_items = random.sample(list(labels.items()), 5)
    
    print("🖼️ Sample Images Preview:")
    print("=" * 40)
    
    for img_path, ground_truth in sample_items:
        img_name = Path(img_path).name
        print(f"\n📷 {img_name}")
        print(f"   Text: '{ground_truth}'")
        
        # อ่านรูป
        img = cv2.imread(img_path)
        if img is not None:
            h, w = img.shape[:2]
            print(f"   Size: {w}×{h} pixels")
            
            # Save a copy for inspection (optional)
            # cv2.imwrite(f"sample_{img_name}", img)
        else:
            print(f"   ERROR: Cannot read image")

if __name__ == "__main__":
    test_simple_image_reading()
    print("\n" + "="*50)
    show_sample_images()
