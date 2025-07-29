#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thai Dataset Generator - Easy Command Helper
ตัวช่วยสร้างคำสั่งสำหรับ optimized generator
"""

import os
import argparse

def print_usage_examples():
    """แสดงตัวอย่างการใช้งาน"""
    print("=" * 60)
    print("🎯 OPTIMIZED THAI GENERATOR - USAGE EXAMPLES")
    print("=" * 60)
    
    print("📖 Basic Usage:")
    print("  python thai_dataset_generator.py <number_of_samples>")
    print()
    
    print("🔍 Show available obstacles:")
    print("  python thai_dataset_generator.py 10 --show-obstacles")
    print()
    
    print("🎨 Quick Examples:")
    print("  python thai_dataset_generator.py 5")
    print("  └─ Create 5 samples per character (fast test)")
    print()
    print("  python thai_dataset_generator.py 10")
    print("  └─ Create 10 samples per character (recommended)")
    print()
    print("  python thai_dataset_generator.py 20")
    print("  └─ Create 20 samples per character (high quality)")
    print()
    print("  python thai_dataset_generator.py 50")
    print("  └─ Create 50 samples per character (production)")
    print()
    
    print("⚙️  Advanced Usage:")
    print("  python thai_dataset_generator.py 15 -d th_dict.txt -o my_dataset")
    print("  └─ Custom dictionary and output folder")
    print()
    print("  python thai_dataset_generator.py 25 -o thai_production_2025")
    print("  └─ Production dataset with custom name")
    print()
    
    print("📊 Optimization Features:")
    print("  ✅ Reduced obstacles from 15 to 8 types")
    print("  ✅ Character visibility enhanced")
    print("  ✅ Gentle transformations only")
    print("  ✅ Better success rate (95%+)")
    print("  ✅ Readable text output")
    print()
    
    print("🎨 Optimized Obstacles:")
    print("  1. rotation: ±2 degrees (was ±10)")
    print("  2. brightness: 0.8-1.2 (was 0.3-1.5)")
    print("  3. contrast: 0.8-1.2 (was 0.5-1.8)")
    print("  4. blur: 0-0.4 (was 0-1.0)")
    print("  5. noise: 0-0.05 (was 0-0.15)")
    print("  6. position: center variants only")
    print("  7. padding: 15-25 pixels")
    print("  8. compression: 85-100% quality")
    print()
    
    print("💡 Tips:")
    print("  • Start with 5-10 samples for testing")
    print("  • Use 15-25 samples for training")
    print("  • Use 30+ samples for production")
    print("  • Check output quality first!")
    print("=" * 60)

def interactive_command_builder():
    """สร้างคำสั่งแบบ interactive"""
    print("\n🎯 INTERACTIVE COMMAND BUILDER")
    print("=" * 40)
    
    # รับจำนวนรูป
    while True:
        try:
            samples = int(input("📊 Enter number of samples per character (5-100): "))
            if 5 <= samples <= 100:
                break
            else:
                print("❌ Please enter a number between 5 and 100")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # รับชื่อ output (optional)
    output_name = input("📁 Enter output folder name (press Enter for auto): ").strip()
    
    # รับ dictionary path (optional)
    dict_path = input("📖 Enter dictionary path (press Enter for default): ").strip()
    
    # สร้างคำสั่ง
    command = f"python optimized_thai_generator.py {samples}"
    
    if dict_path:
        command += f" -d {dict_path}"
    
    if output_name:
        command += f" -o {output_name}"
    
    print("\n🚀 Generated Command:")
    print("=" * 40)
    print(command)
    print("=" * 40)
    
    # ถามว่าจะรันเลยหรือไม่
    run_now = input("\n▶️  Run this command now? (y/n): ").strip().lower()
    if run_now in ['y', 'yes']:
        print("\n🚀 Running command...")
        os.system(command)
    else:
        print("💾 Copy the command above to run it manually")

def quick_commands():
    """แสดงคำสั่งที่ใช้บ่อย"""
    print("\n⚡ QUICK COMMANDS")
    print("=" * 40)
    print("Copy and paste these commands:")
    print()
    
    commands = [
        ("🧪 Test (5 samples)", "python thai_dataset_generator.py 5"),
        ("📊 Standard (10 samples)", "python thai_dataset_generator.py 10"),
        ("🎯 Training (20 samples)", "python thai_dataset_generator.py 20"),
        ("🏭 Production (50 samples)", "python thai_dataset_generator.py 50"),
        ("🔍 Show obstacles", "python thai_dataset_generator.py 10 --show-obstacles")
    ]
    
    for desc, cmd in commands:
        print(f"{desc}:")
        print(f"  {cmd}")
        print()

def main():
    parser = argparse.ArgumentParser(description='Thai Dataset Generator Helper')
    parser.add_argument('--examples', action='store_true', help='Show usage examples')
    parser.add_argument('--interactive', action='store_true', help='Interactive command builder')
    parser.add_argument('--quick', action='store_true', help='Show quick commands')
    
    args = parser.parse_args()
    
    if args.examples:
        print_usage_examples()
    elif args.interactive:
        interactive_command_builder()
    elif args.quick:
        quick_commands()
    else:
        # แสดงทุกอย่าง
        print_usage_examples()
        quick_commands()
        
        print("\n🤔 Want to build a custom command?")
        choice = input("Run interactive builder? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            interactive_command_builder()

if __name__ == "__main__":
    main()
