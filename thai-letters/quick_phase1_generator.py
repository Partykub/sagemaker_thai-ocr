#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Quick Thai Dataset Generator - Easy Interface
สำหรับการสร้าง dataset ภาษาไทยแบบง่าย ๆ 

Usage:
    python quick_phase1_generator.py 10    # สร้าง 10 samples ต่อตัวอักษร
    python quick_phase1_generator.py 20    # สร้าง 20 samples ต่อตัวอักษร
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def main():
    """Quick interface for Phase 1 dataset generation"""
    
    print("🔥 Quick Thai Dataset Generator - Phase 1")
    print("=" * 50)
    
    # Get samples count from command line
    if len(sys.argv) < 2:
        print("Usage: python quick_phase1_generator.py <samples_per_char>")
        print("Example: python quick_phase1_generator.py 10")
        sys.exit(1)
    
    try:
        samples = int(sys.argv[1])
    except ValueError:
        print("❌ Error: samples_per_char must be a number")
        sys.exit(1)
    
    if samples < 1 or samples > 100:
        print("❌ Error: samples_per_char must be between 1-100")
        sys.exit(1)
    
    print(f"📊 Generating {samples} samples per Thai character...")
    
    # Import and run the main generator
    try:
        from phase1_thai_dataset_complete import ThaiDatasetPhase1
        
        # Initialize generator
        generator = ThaiDatasetPhase1(
            samples_per_char=samples,
            train_val_split=0.8
        )
        
        # Generate dataset
        success = generator.generate_complete_dataset()
        
        if success:
            print("\n🎉 Dataset generation completed successfully!")
            print(f"📁 Check output directory: {generator.output_dir}")
            
            # Show quick stats
            print(f"\n📊 Quick Stats:")
            print(f"   - Total images: {generator.stats['total_images']:,}")
            print(f"   - Train images: {generator.stats['train_images']:,}")
            print(f"   - Val images: {generator.stats['val_images']:,}")
            print(f"   - Success rate: {generator.stats['success_rate']:.1f}%")
            
        else:
            print("❌ Dataset generation failed!")
            sys.exit(1)
    
    except ImportError as e:
        print(f"❌ Error importing generator: {e}")
        print("Make sure phase1_thai_dataset_complete.py is in the same directory")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
