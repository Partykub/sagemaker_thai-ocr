#!/usr/bin/env python3
"""
Dataset Detection Helper: หาไฟล์ dataset และ validation data สำหรับการทดสอบ
"""

import os
from pathlib import Path
from typing import List, Dict, Optional

def find_datasets() -> Dict[str, List[Path]]:
    """หา dataset ทั้งหมดในโปรเจค"""
    
    project_root = Path(__file__).parent.parent.parent
    datasets = {
        "converted": [],
        "raw": [],
        "output": []
    }
    
    print("🔍 Searching for datasets...")
    
    # หาใน thai-letters/datasets
    thai_letters_datasets = project_root / "thai-letters" / "datasets"
    if thai_letters_datasets.exists():
        print(f"📁 Checking: {thai_letters_datasets}")
        
        for item in thai_letters_datasets.iterdir():
            if item.is_dir():
                if "converted" in item.name or "paddleocr" in item.name:
                    datasets["converted"].append(item)
                    print(f"   ✅ Found converted dataset: {item.name}")
                else:
                    datasets["raw"].append(item)
                    print(f"   📊 Found raw dataset: {item.name}")
    
    # หาใน train_data_thai_paddleocr_* folders
    for item in project_root.iterdir():
        if item.is_dir() and item.name.startswith("train_data_thai_paddleocr"):
            datasets["converted"].append(item)
            print(f"   ✅ Found converted dataset: {item.name}")
    
    # หาใน output folders
    output_dir = project_root / "output"
    if output_dir.exists():
        for item in output_dir.iterdir():
            if item.is_dir():
                datasets["output"].append(item)
                print(f"   📈 Found output dataset: {item.name}")
    
    return datasets

def analyze_dataset_structure(dataset_path: Path) -> Dict:
    """วิเคราะห์โครงสร้างของ dataset"""
    
    analysis = {
        "path": str(dataset_path),
        "name": dataset_path.name,
        "total_size": 0,
        "directories": [],
        "label_files": [],
        "image_folders": [],
        "config_files": [],
        "sample_count": 0
    }
    
    if not dataset_path.exists():
        return analysis
    
    print(f"\n📊 Analyzing: {dataset_path.name}")
    
    # หาไฟล์และโฟลเดอร์สำคัญ
    for root, dirs, files in os.walk(dataset_path):
        root_path = Path(root)
        
        # นับขนาดไฟล์
        for file in files:
            file_path = root_path / file
            try:
                analysis["total_size"] += file_path.stat().st_size
            except:
                pass
            
            # หาไฟล์ label
            if file.endswith(('.txt', '.json')) and any(keyword in file.lower() 
                for keyword in ['label', 'gt', 'train', 'val', 'test']):
                analysis["label_files"].append(str(file_path.relative_to(dataset_path)))
                
                # นับจำนวนตัวอย่างในไฟล์ label
                try:
                    if file.endswith('.txt'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            analysis["sample_count"] += len([l for l in lines if l.strip()])
                except:
                    pass
            
            # หาไฟล์ config
            if file.endswith(('.yml', '.yaml', '.json', '.cfg')):
                analysis["config_files"].append(str(file_path.relative_to(dataset_path)))
        
        # หาโฟลเดอร์รูปภาพ
        for dir_name in dirs:
            dir_path = root_path / dir_name
            if any(keyword in dir_name.lower() for keyword in ['image', 'img', 'pic', 'train', 'val', 'test']):
                # นับจำนวนรูปในโฟลเดอร์
                try:
                    image_count = len([f for f in os.listdir(dir_path) 
                                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
                    if image_count > 0:
                        analysis["image_folders"].append({
                            "path": str(dir_path.relative_to(dataset_path)),
                            "image_count": image_count
                        })
                except:
                    pass
    
    # แปลงขนาดให้อ่านง่าย
    size_mb = analysis["total_size"] / (1024 * 1024)
    print(f"   📏 Size: {size_mb:.1f} MB")
    print(f"   📄 Label files: {len(analysis['label_files'])}")
    print(f"   🖼️ Image folders: {len(analysis['image_folders'])}")
    print(f"   📊 Sample count: {analysis['sample_count']}")
    
    return analysis

def find_best_dataset_for_testing() -> Optional[Path]:
    """หา dataset ที่เหมาะสมที่สุดสำหรับการทดสอบ"""
    
    datasets = find_datasets()
    
    if not datasets["converted"]:
        print("❌ No converted datasets found!")
        return None
    
    print(f"\n🎯 Found {len(datasets['converted'])} converted dataset(s)")
    
    best_dataset = None
    best_score = 0
    
    for dataset_path in datasets["converted"]:
        analysis = analyze_dataset_structure(dataset_path)
        
        # คำนวณคะแนนตาม criteria
        score = 0
        
        # มี label files หรือไม่
        if analysis["label_files"]:
            score += 10
            
        # มีรูปภาพหรือไม่
        if analysis["image_folders"]:
            score += 10
            
        # จำนวน samples
        if analysis["sample_count"] > 0:
            score += min(analysis["sample_count"] / 100, 10)  # max 10 points
            
        # ขนาดไฟล์ (ไม่ใหญ่เกินไป)
        size_mb = analysis["total_size"] / (1024 * 1024)
        if 10 < size_mb < 500:  # ขนาดเหมาะสม
            score += 5
        
        print(f"   🏆 Score for {dataset_path.name}: {score:.1f}")
        
        if score > best_score:
            best_score = score
            best_dataset = dataset_path
    
    if best_dataset:
        print(f"\n✅ Best dataset for testing: {best_dataset.name}")
        print(f"   📍 Path: {best_dataset}")
    
    return best_dataset

def main():
    """ฟังก์ชันหลัก"""
    print("🔍 Thai OCR Dataset Detection")
    print("=" * 50)
    
    best_dataset = find_best_dataset_for_testing()
    
    if best_dataset:
        print(f"\n📋 Detailed analysis of recommended dataset:")
        detailed_analysis = analyze_dataset_structure(best_dataset)
        
        print(f"\n🎯 Ready for testing!")
        print(f"   Use this path in your testing script:")
        print(f"   {best_dataset}")
        
        # แสดงไฟล์ label ที่พบ
        if detailed_analysis["label_files"]:
            print(f"\n📄 Available label files:")
            for label_file in detailed_analysis["label_files"]:
                print(f"   - {label_file}")
        
        # แสดงโฟลเดอร์รูปที่พบ
        if detailed_analysis["image_folders"]:
            print(f"\n🖼️ Available image folders:")
            for img_folder in detailed_analysis["image_folders"]:
                print(f"   - {img_folder['path']} ({img_folder['image_count']} images)")
    
    else:
        print(f"\n❌ No suitable dataset found for testing!")
        print(f"   Please check if datasets are properly converted to PaddleOCR format.")

if __name__ == "__main__":
    main()
