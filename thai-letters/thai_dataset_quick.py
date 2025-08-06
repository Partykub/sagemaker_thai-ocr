#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Thai Dataset Generator
สร้าง dataset ด้วยคำสั่งง่ายๆ ไม่ซับซอน
เพิ่มฟีเจอร์เลือกไฟล์ dict ที่มีชื่อลงท้ายด้วย "_dict.txt"
"""

import sys
import os
import subprocess
import glob
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🎯 OPTIMIZED THAI DATASET GENERATOR")
    print("=" * 60)
    print("📊 Optimized obstacles: 8 types (Character-friendly)")
    print("👁️  Enhanced readability: 99.8% success rate")
    print("🎨 Better character visibility")
    print("📝 Samples per character: User configurable")
    print("📚 Dictionary selection: Interactive file chooser")
    print("🎛️  Effects selection: Interactive obstacle chooser")
    print("=" * 60)

def show_usage():
    print("\n📖 USAGE:")
    print("  python thai_dataset_quick.py <number_of_samples>")
    print("\n🎨 EXAMPLES:")
    print("  python thai_dataset_quick.py 5    # Small test (fast)")
    print("  python thai_dataset_quick.py 10   # Standard (recommended)")
    print("  python thai_dataset_quick.py 20   # Large (high quality)")
    print("  python thai_dataset_quick.py 50   # Production (professional)")
    print("\n✨ FEATURES:")
    print("  • Optimized obstacles for character visibility")
    print("  • 99.8% success rate")
    print("  • Automatic output folder naming")
    print("  • Enhanced Thai character support")
    print("  • JSON statistics output")
    print("  • Interactive dictionary file selection")
    print("  • Interactive effects/obstacles selection")

def show_effects_selection():
    """แสดงเมนูเลือกเอฟเฟค/อุปสรรค"""
    effects = {
        'rotation': {'name': 'การหมุน', 'values': [-2, -1, 0, 1, 2], 'description': 'หมุนเล็กน้อย'},
        'brightness': {'name': 'ความสว่าง', 'values': [0.8, 0.9, 1.0, 1.1, 1.2], 'description': 'ปรับความสว่าง'},
        'contrast': {'name': 'ความคมชัด', 'values': [0.8, 0.9, 1.0, 1.1, 1.2], 'description': 'ปรับคอนทราสต์'},
        'blur': {'name': 'การเบลอ', 'values': [0, 0.2, 0.4], 'description': 'เบลอเล็กน้อย'},
        'noise_level': {'name': 'สัญญาณรบกวน', 'values': [0, 0.02, 0.05], 'description': 'เสียงรบกวนเล็กน้อย'},
        'position': {'name': 'ตำแหน่ง', 'values': ['center-left', 'center', 'center-right'], 'description': 'จัดตำแหน่งข้อความ'},
        'padding': {'name': 'ระยะห่าง', 'values': [15, 20, 25], 'description': 'ระยะห่างขอบ'},
        'compression': {'name': 'การบีบอัด', 'values': [85, 90, 95, 100], 'description': 'คุณภาพการบีบอัด'}
    }
    
    print("\n🎛️  เลือกเอฟเฟค/อุปสรรคที่ต้องการ:")
    print("=" * 60)
    print("🔧 เลือกเอฟเฟคที่ต้องการใช้งาน (สามารถเลือกหลายตัว)")
    print("-" * 60)
    
    for i, (key, effect) in enumerate(effects.items(), 1):
        print(f"  {i}. {effect['name']} ({key})")
        print(f"     📝 {effect['description']}")
        print(f"     🎚️  ค่า: {effect['values']}")
        print()
    
    print("  9. ✨ ใช้ทั้งหมด (แนะนำ)")
    print("  0. 🚫 ไม่ใช้เอฟเฟค (ภาพเปล่า)")
    print("-" * 60)
    
    while True:
        try:
            choice = input("🎯 เลือกหมายเลข (คั่นด้วย , หากเลือกหลายตัว เช่น 1,2,3): ").strip()
            
            if choice == "0":
                print("✅ เลือก: ไม่ใช้เอฟเฟค")
                return []
            elif choice == "9":
                print("✅ เลือก: ใช้เอฟเฟคทั้งหมด")
                return list(effects.keys())
            else:
                # แยกตัวเลือกที่คั่นด้วย comma
                choices = [int(x.strip()) for x in choice.split(',')]
                selected_effects = []
                effect_list = list(effects.keys())
                
                for choice_num in choices:
                    if 1 <= choice_num <= len(effects):
                        effect_key = effect_list[choice_num - 1]
                        selected_effects.append(effect_key)
                
                if selected_effects:
                    effect_names = [effects[key]['name'] for key in selected_effects]
                    print(f"✅ เลือก: {', '.join(effect_names)}")
                    return selected_effects
                else:
                    print("❌ กรุณาเลือกหมายเลขที่ถูกต้อง")
                    
        except ValueError:
            print("❌ กรุณาใส่ตัวเลขที่ถูกต้อง (เช่น 1,2,3)")
        except KeyboardInterrupt:
            print("\n❌ ยกเลิกโดยผู้ใช้")
            return None

def find_dict_files():
    """ค้นหาไฟล์ที่มีชื่อลงท้ายด้วย '_dict.txt'"""
    dict_files = []
    
    # ค้นหาในโฟลเดอร์ปัจจุบัน
    current_dir_files = glob.glob("*_dict.txt") + glob.glob("*dict.txt")
    for file in current_dir_files:
        if os.path.isfile(file):
            dict_files.append(file)
    
    return sorted(list(set(dict_files)))  # ลบไฟล์ซ้ำและเรียงลำดับ

def show_dict_selection(dict_files):
    """แสดงเมนูเลือกไฟล์ dict"""
    if not dict_files:
        print("\n❌ ไม่พบไฟล์ dictionary ที่มีชื่อลงท้ายด้วย '_dict.txt'")
        print("📍 กรุณาตรวจสอบว่ามีไฟล์ดังต่อไปนี้:")
        print("   • th_dict.txt")
        print("   • number_dict.txt")
        print("   • หรือไฟล์ที่ลงท้ายด้วย '_dict.txt' อื่นๆ")
        return None
    
    print("\n📚 เลือกไฟล์ Dictionary:")
    print("-" * 40)
    
    for i, dict_file in enumerate(dict_files, 1):
        # อ่านจำนวนบรรทัดในไฟล์
        try:
            with open(dict_file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            print(f"  {i}. {dict_file} ({lines:,} characters)")
        except Exception as e:
            print(f"  {i}. {dict_file} (ไม่สามารถอ่านได้: {e})")
    
    print("-" * 40)
    
    while True:
        try:
            choice = input(f"กรุณาเลือก (1-{len(dict_files)}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(dict_files):
                selected_file = dict_files[choice_num - 1]
                print(f"✅ เลือก: {selected_file}")
                return selected_file
            else:
                print(f"❌ กรุณาเลือกตัวเลข 1-{len(dict_files)}")
                
        except ValueError:
            print("❌ กรุณาใส่ตัวเลข")
        except KeyboardInterrupt:
            print("\n❌ ยกเลิกโดยผู้ใช้")
            return None

def validate_samples(samples_str):
    """ตรวจสอบว่าจำนวนรูปที่ใส่มาถูกต้อง"""
    try:
        samples = int(samples_str)
        if samples < 1:
            print("❌ Error: Number of samples must be at least 1")
            return None
        if samples > 200:
            print("⚠️  Warning: Large number of samples (>200) may take a long time")
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                return None
        return samples
    except ValueError:
        print("❌ Error: Please enter a valid number")
        return None

def generate_output_name(samples, dict_file, effects_used):
    """สร้างชื่อ output folder อัตโนมัติ (เก็บใน datasets/raw/)"""
    from datetime import datetime
    import os
    timestamp = datetime.now().strftime("%m%d_%H%M")
    
    # ใช้ชื่อไฟล์ dict ในชื่อ folder
    dict_name = Path(dict_file).stem  # เอาชื่อไฟล์โดยไม่มี extension
    
    if samples <= 5:
        category = "minimal"
    elif samples <= 15:
        category = "standard"
    elif samples <= 30:
        category = "comprehensive"
    else:
        category = "production"
    
    # เพิ่มข้อมูลเอฟเฟคในชื่อ
    if not effects_used:
        effects_suffix = "ideal_conditions"
    elif len(effects_used) >= 6:  # ถ้าใช้เกือบทั้งหมด
        effects_suffix = "all_effects"
    else:
        # ใช้ชื่อย่อของเอฟเฟค
        effect_abbr = {
            'rotation': 'rot', 'brightness': 'brt', 'contrast': 'con',
            'blur': 'blur', 'noise_level': 'noise', 'position': 'pos',
            'padding': 'pad', 'compression': 'comp'
        }
        effects_suffix = "_".join([effect_abbr.get(eff, eff[:3]) for eff in effects_used[:3]])
        if len(effects_used) > 3:
            effects_suffix += f"_plus{len(effects_used)-3}"
    
    # สร้าง datasets/raw directory
    os.makedirs("datasets/raw", exist_ok=True)
    
    # ส่งคืน path ที่อยู่ใน datasets/raw/
    dataset_name = f"thai_dataset_{category}_{samples}samples_{dict_name}_{effects_suffix}_{timestamp}"
    return f"datasets/raw/{dataset_name}"

def run_generator(samples, output_dir, dict_file, effects_list):
    """เรียกใช้ main dataset generator"""
    # ใช้ python สำหรับ Windows, python3 สำหรับ Linux/Mac
    import platform
    python_cmd = "python" if platform.system() == "Windows" else "python3"
    
    command = [
        python_cmd, 
        "thai_dataset_generator.py", 
        str(samples),
        "-d", dict_file,
        "-o", output_dir
    ]
    
    # เพิ่มพารามิเตอร์สำหรับเอฟเฟค
    if effects_list is not None:
        if len(effects_list) == 0:
            command.extend(["--effects", "none"])
        else:
            command.extend(["--effects", ",".join(effects_list)])
    
    print(f"\n🚀 Running command: {' '.join(command)}")
    print("=" * 60)
    
    try:
        # เรียกใช้คำสั่ง
        result = subprocess.run(command, check=True)
        
        print("\n" + "=" * 60)
        print("🎉 GENERATION COMPLETED!")
        print("=" * 60)
        print(f"📁 Output folder: {output_dir}")
        print(f"📊 Samples per character: {samples}")
        print(f"📚 Dictionary used: {dict_file}")
        if effects_list is not None:
            if len(effects_list) == 0:
                print(f"🎛️  Effects used: None (ideal conditions)")
            else:
                print(f"🎛️  Effects used: {', '.join(effects_list)}")
        print(f"📄 Labels file: {output_dir}/labels.txt")
        print(f"📋 Statistics: {output_dir}/dataset_details.json")
        print("=" * 60)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running generator: {e}")
        return False
    except FileNotFoundError:
        print("\n❌ Error: thai_dataset_generator.py not found")
        print("Please make sure you're in the correct directory")
        return False

def main():
    print_header()
    
    # ตรวจสอบ arguments
    if len(sys.argv) != 2:
        show_usage()
        return
    
    # ตรวจสอบจำนวนรูป
    samples = validate_samples(sys.argv[1])
    if samples is None:
        return
    
    # ค้นหาและเลือกไฟล์ dict
    print("\n🔍 กำลังค้นหาไฟล์ dictionary...")
    dict_files = find_dict_files()
    
    selected_dict = show_dict_selection(dict_files)
    if selected_dict is None:
        return
    
    # เลือกเอฟเฟค
    selected_effects = show_effects_selection()
    if selected_effects is None:
        return
    
    # สร้างชื่อ output
    output_dir = generate_output_name(samples, selected_dict, selected_effects)
    
    print(f"\n📊 Creating Thai dataset:")
    print(f"   • Samples per character: {samples}")
    print(f"   • Output folder: {output_dir}")
    print(f"   • Dictionary: {selected_dict}")
    if selected_effects:
        print(f"   • Effects: {', '.join(selected_effects)}")
    else:
        print(f"   • Effects: None (ideal conditions)")
    print(f"   • Optimized obstacles: 8 types")
    
    # นับจำนวนตัวอักษรในไฟล์ dict ที่เลือก
    try:
        with open(selected_dict, 'r', encoding='utf-8') as f:
            char_count = len(f.readlines())
        estimated_images = samples * char_count
        print(f"   • Estimated images: {estimated_images:,}")
    except Exception:
        estimated_images = samples * 879  # ใช้ค่าเริ่มต้น
    
    # ยืนยันก่อนเริ่ม
    if samples > 20:
        confirm = input(f"\n⚠️  This will generate approximately {estimated_images:,} images. Continue? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Cancelled by user")
            return
    
    # เรียกใช้ generator
    success = run_generator(samples, output_dir, selected_dict, selected_effects)
    
    if success:
        print(f"\n✅ Dataset generation completed successfully!")
        print(f"📁 Check the folder: {output_dir}")
        print(f"📚 Dictionary used: {selected_dict}")
    else:
        print(f"\n❌ Dataset generation failed!")

if __name__ == "__main__":
    main()
