#!/usr/bin/env python3
"""
Visual Inspection of Validation Images
ตรวจสอบรูปภาพ validation ด้วยตา
"""

import os
import logging
from pathlib import Path
import shutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def read_validation_data():
    """อ่านข้อมูล validation"""
    
    val_file = "thai-letters/datasets/converted/train_data_thai_paddleocr_0806_1433/train_data/rec/rec_gt_val.txt"
    
    if not os.path.exists(val_file):
        logger.error(f"❌ Validation file not found: {val_file}")
        return []
    
    logger.info(f"📖 Reading validation data from: {val_file}")
    
    validation_data = []
    base_dir = "thai-letters/datasets/converted/train_data_thai_paddleocr_0806_1433/train_data/rec"
    
    with open(val_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    image_path = parts[0]
                    true_label = parts[1]
                    
                    full_image_path = os.path.join(base_dir, image_path)
                    
                    if os.path.exists(full_image_path):
                        # ตรวจสอบขนาดไฟล์
                        file_size = os.path.getsize(full_image_path)
                        
                        validation_data.append({
                            'image_path': full_image_path,
                            'relative_path': image_path,
                            'true_label': true_label,
                            'line_num': line_num,
                            'file_size': file_size
                        })
    
    logger.info(f"✅ Found {len(validation_data)} validation samples")
    return validation_data

def copy_sample_images():
    """คัดลอกรูปภาพตัวอย่างมาให้ดู"""
    
    validation_data = read_validation_data()
    
    if not validation_data:
        logger.error("❌ No validation data found")
        return
    
    # สร้างโฟลเดอร์สำหรับรูปตัวอย่าง
    sample_dir = "validation_samples"
    os.makedirs(sample_dir, exist_ok=True)
    
    # คัดลอกรูป 10 รูปแรก
    sample_count = min(10, len(validation_data))
    
    logger.info(f"📋 Copying {sample_count} sample images to {sample_dir}/")
    logger.info("-" * 60)
    
    for i, sample in enumerate(validation_data[:sample_count], 1):
        src_path = sample['image_path']
        true_label = sample['true_label']
        file_size = sample['file_size']
        
        # สร้างชื่อไฟล์ใหม่ที่มี label
        original_name = os.path.basename(src_path)
        name_parts = original_name.split('.')
        new_name = f"{i:02d}_{name_parts[0]}_label_{true_label}.{name_parts[-1]}"
        
        dst_path = os.path.join(sample_dir, new_name)
        
        try:
            shutil.copy2(src_path, dst_path)
            logger.info(f"[{i:2d}] {original_name} → {new_name}")
            logger.info(f"     Label: '{true_label}' | Size: {file_size} bytes")
            
        except Exception as e:
            logger.error(f"     ❌ Failed to copy: {str(e)}")
    
    logger.info("-" * 60)
    logger.info(f"✅ Sample images copied to: {sample_dir}/")
    logger.info("🔍 Please visually inspect these images to verify the labels")

def analyze_validation_data():
    """วิเคราะห์ข้อมูล validation"""
    
    validation_data = read_validation_data()
    
    if not validation_data:
        return
    
    logger.info("📊 VALIDATION DATA ANALYSIS")
    logger.info("-" * 60)
    
    # นับจำนวนแต่ละตัวเลข
    label_counts = {}
    total_size = 0
    
    for sample in validation_data:
        label = sample['true_label']
        size = sample['file_size']
        
        label_counts[label] = label_counts.get(label, 0) + 1
        total_size += size
    
    # แสดงสถิติ
    logger.info(f"📊 Total samples: {len(validation_data)}")
    logger.info(f"📦 Total size: {total_size / 1024:.1f} KB")
    logger.info(f"📏 Average size: {total_size / len(validation_data):.0f} bytes")
    
    logger.info("\n📈 Label distribution:")
    for label in sorted(label_counts.keys()):
        count = label_counts[label]
        percentage = (count / len(validation_data)) * 100
        logger.info(f"   '{label}': {count} samples ({percentage:.1f}%)")
    
    # แสดงตัวอย่างไฟล์แต่ละ label
    logger.info("\n📋 Sample files for each label:")
    for label in sorted(label_counts.keys()):
        samples_for_label = [s for s in validation_data if s['true_label'] == label]
        sample_file = samples_for_label[0] if samples_for_label else None
        
        if sample_file:
            logger.info(f"   '{label}': {sample_file['relative_path']} ({sample_file['file_size']} bytes)")

def create_simple_test_report():
    """สร้างรายงานง่ายๆ"""
    
    validation_data = read_validation_data()
    
    if not validation_data:
        return
    
    report_file = "validation_data_report.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("THAI NUMBERS OCR - VALIDATION DATA REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Dataset: train_data_thai_paddleocr_0806_1433\n")
        f.write(f"Total validation samples: {len(validation_data)}\n")
        f.write(f"Date: 2025-08-07\n\n")
        
        f.write("SAMPLE DATA (First 20 samples):\n")
        f.write("-" * 30 + "\n")
        
        for i, sample in enumerate(validation_data[:20], 1):
            f.write(f"{i:2d}. {sample['relative_path']} → '{sample['true_label']}' ({sample['file_size']} bytes)\n")
        
        if len(validation_data) > 20:
            f.write(f"... and {len(validation_data) - 20} more samples\n")
        
        f.write("\nLABEL DISTRIBUTION:\n")
        f.write("-" * 20 + "\n")
        
        label_counts = {}
        for sample in validation_data:
            label = sample['true_label']
            label_counts[label] = label_counts.get(label, 0) + 1
        
        for label in sorted(label_counts.keys()):
            count = label_counts[label]
            percentage = (count / len(validation_data)) * 100
            f.write(f"'{label}': {count} samples ({percentage:.1f}%)\n")
    
    logger.info(f"📝 Report saved to: {report_file}")

def main():
    """Main function"""
    
    logger.info("🔍 Visual Inspection of Validation Images")
    logger.info("=" * 60)
    
    # วิเคราะห์ข้อมูล
    analyze_validation_data()
    
    # คัดลอกรูปตัวอย่าง
    copy_sample_images()
    
    # สร้างรายงาน
    create_simple_test_report()
    
    logger.info("\n💡 NEXT STEPS:")
    logger.info("1. Check the 'validation_samples/' folder")
    logger.info("2. Verify that image labels match the actual numbers")
    logger.info("3. If labels are correct, we can proceed with model testing")
    logger.info("4. Read 'validation_data_report.txt' for detailed statistics")
    
    return 0

if __name__ == '__main__':
    exit(main())
