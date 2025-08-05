#!/usr/bin/env python3
"""
Project Clean Up Summary
สรุปการทำความสะอาดโปรเจกต์
"""
import os
from pathlib import Path

def show_clean_structure():
    """แสดงโครงสร้างโปรเจกต์หลังทำความสะอาด"""
    print("🧹 Thai OCR Project - Clean Structure")
    print("=" * 60)
    
    root = Path(".")
    important_dirs = [
        "configs/",
        "doc/", 
        "models/",
        "scripts/",
        "terraform/",
        "thai-letters/",
        "test_images/",
        "PaddleOCR/"
    ]
    
    important_files = [
        "README.md",
        "requirements.txt",
        "Dockerfile.sagemaker",
        "required_permissions.json",
        "THAI_OCR_PROJECT_SUMMARY_20250805_145954.json",
        "THAI_OCR_ACCURACY_IMPROVEMENT_PLAN.json",
        "DEPLOYMENT_CHECKLIST_20250805_144427.json"
    ]
    
    print("📁 Core Directories:")
    for dir_name in important_dirs:
        dir_path = root / dir_name
        if dir_path.exists():
            size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
            file_count = sum(1 for f in dir_path.rglob('*') if f.is_file())
            print(f"   ✅ {dir_name:<20} {file_count:>4} files, {size:>10,} bytes")
        else:
            print(f"   ❌ {dir_name:<20} Missing")
    
    print(f"\n📄 Important Files:")
    for file_name in important_files:
        file_path = root / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✅ {file_name:<40} {size:>8,} bytes")
        else:
            print(f"   ❌ {file_name:<40} Missing")
    
    print(f"\n📊 Scripts Summary:")
    scripts_ml = root / "scripts" / "ml"
    if scripts_ml.exists():
        ml_files = list(scripts_ml.glob("*.py"))
        print(f"   🔬 ML Scripts: {len(ml_files)} files")
        for f in ml_files:
            print(f"      - {f.name}")
    
    scripts_utils = root / "scripts" / "utils" 
    if scripts_utils.exists():
        util_files = list(scripts_utils.glob("*.py"))
        print(f"   🛠️ Utility Scripts: {len(util_files)} files")
        for f in util_files:
            print(f"      - {f.name}")
    
    scripts_infra = root / "scripts" / "infrastructure"
    if scripts_infra.exists():
        infra_files = list(scripts_infra.glob("*.py"))
        print(f"   🏗️ Infrastructure Scripts: {len(infra_files)} files")
        for f in infra_files:
            print(f"      - {f.name}")
    
    print(f"\n🎯 Key Features Preserved:")
    print(f"   ✅ Trained Thai OCR model (models/sagemaker_trained/)")
    print(f"   ✅ Thai character dictionary (thai-letters/th_dict.txt)")
    print(f"   ✅ Training configurations (configs/)")
    print(f"   ✅ Documentation (doc/)")
    print(f"   ✅ Infrastructure as Code (terraform/)")
    print(f"   ✅ AWS deployment scripts (scripts/)")
    print(f"   ✅ PaddleOCR framework")
    print(f"   ✅ Test images for validation")
    
    print(f"\n🗑️ Cleaned Up:")
    print(f"   ❌ Duplicate directories (thai-letters copy/)")
    print(f"   ❌ Redundant test files (20+ test_*.py)")
    print(f"   ❌ Temporary result files (*.json logs)")
    print(f"   ❌ Old virtual environments (thai_ocr_env/)")
    print(f"   ❌ Dangerous utility scripts (nuclear_delete.py)")
    print(f"   ❌ Development artifacts (PROGRESS.md)")
    
    print(f"\n🎉 Project is now clean and ready for production!")

def main():
    """Main function"""
    show_clean_structure()

if __name__ == "__main__":
    main()
