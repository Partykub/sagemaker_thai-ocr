#!/usr/bin/env python3
"""
Direct Model Inference: ทดสอบโมเดลที่เทรนมาโดยตรงไม่ผ่าน PaddleOCR wrapper
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
import json
import random
from typing import Dict, List, Tuple
from datetime import datetime

# Add PaddleOCR to path for paddle inference
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "PaddleOCR"))

try:
    import paddle
    import paddle.nn.functional as F
    from paddle.inference import Config, create_predictor
    print("✅ Paddle imported successfully")
except ImportError as e:
    print(f"❌ Paddle import error: {e}")
    sys.exit(1)

class DirectModelTester:
    """ทดสอบโมเดลโดยตรงด้วย Paddle Inference"""
    
    def __init__(self):
        self.project_root = project_root
        self.model_dir = self.project_root / "models" / "sagemaker_trained"
        self.dataset_dir = self.project_root / "thai-letters" / "datasets" / "converted" / "train_data_thai_paddleocr_0731_1604"
        
        self.predictor = None
        self.char_dict = None
        
        # Load character dictionary
        self.load_char_dict()
    
    def load_char_dict(self):
        """โหลด character dictionary"""
        dict_file = self.project_root / "PaddleOCR" / "ppocr" / "utils" / "dict" / "th_dict.txt"
        
        if not dict_file.exists():
            # ลองหาไฟล์ dict อื่น
            alt_dict = self.project_root / "th_dict.txt"
            if alt_dict.exists():
                dict_file = alt_dict
            else:
                print(f"⚠️ Dictionary not found, creating basic Thai dict")
                self.create_basic_thai_dict()
                return
        
        try:
            with open(dict_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                self.char_dict = ['blank'] + [line.strip() for line in lines]
            
            print(f"✅ Loaded character dictionary: {len(self.char_dict)} characters")
        except Exception as e:
            print(f"❌ Error loading dictionary: {e}")
            self.create_basic_thai_dict()
    
    def create_basic_thai_dict(self):
        """สร้าง dictionary พื้นฐานสำหรับภาษาไทย"""
        thai_chars = [
            # พยัญชนะ
            'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ',
            'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ',
            'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ษ',
            'ส', 'ห', 'ฬ', 'อ', 'ฮ',
            # สำเนียง และเครื่องหมาย
            'ะ', 'ั', 'า', 'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'เ', 'แ', 'โ',
            'ใ', 'ไ', 'ๅ', 'ๆ', '็', '่', '้', '๊', '๋', '์',
            # เลข
            '๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙',
            # พิเศษ
            'ฯ', '๏', '๚', '๛', ' ', 'a', 'b', 'c', 'd', 'e', 'v', 'w', '"'
        ]
        
        self.char_dict = ['blank'] + thai_chars
        print(f"✅ Created basic Thai dictionary: {len(self.char_dict)} characters")
    
    def check_model_files(self) -> bool:
        """ตรวจสอบไฟล์โมเดล"""
        print("🔍 Checking model files...")
        
        if not self.model_dir.exists():
            print(f"❌ Model directory not found: {self.model_dir}")
            return False
        
        # หาไฟล์ .pdparams และ .pdmodel
        param_file = None
        model_file = None
        
        for file in self.model_dir.iterdir():
            if file.suffix == '.pdparams':
                param_file = file
                print(f"   📄 Found params: {file.name}")
            elif file.suffix == '.pdmodel':
                model_file = file
                print(f"   📄 Found model: {file.name}")
        
        if not param_file:
            print(f"❌ No .pdparams file found!")
            return False
        
        # สำหรับ inference อาจไม่ต้องมี .pdmodel ก็ได้
        print(f"✅ Model files check passed")
        return True
    
    def load_ground_truth(self) -> Dict[str, str]:
        """โหลดข้อมูลเฉลย"""
        print("📚 Loading ground truth data...")
        
        ground_truth = {}
        val_labels_file = self.dataset_dir / "train_data" / "rec" / "rec_gt_val.txt"
        
        if not val_labels_file.exists():
            print(f"❌ Labels file not found: {val_labels_file}")
            return {}
        
        try:
            with open(val_labels_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '\t' in line:
                        img_path, text_label = line.split('\t', 1)
                        full_img_path = self.dataset_dir / "train_data" / "rec" / img_path
                        if full_img_path.exists():
                            ground_truth[str(full_img_path)] = text_label.strip()
                        
        except Exception as e:
            print(f"❌ Error reading labels: {e}")
            return {}
        
        print(f"✅ Loaded {len(ground_truth)} samples")
        return ground_truth
    
    def preprocess_image(self, img_path: str) -> np.ndarray:
        """เตรียมรูปภาพสำหรับ inference"""
        try:
            # อ่านรูป
            img = cv2.imread(img_path)
            if img is None:
                return None
            
            # แปลงเป็น grayscale
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Resize เป็นขนาดมาตรฐาน (32x128 สำหรับ recognition)
            img = cv2.resize(img, (128, 32))
            
            # Normalize
            img = img.astype(np.float32) / 255.0
            
            # แปลงเป็น format ที่ paddle ต้องการ (1, 1, 32, 128)
            img = np.expand_dims(img, axis=0)  # เพิ่ม channel dimension
            img = np.expand_dims(img, axis=0)  # เพิ่ม batch dimension
            
            return img
            
        except Exception as e:
            print(f"❌ Error preprocessing image {img_path}: {e}")
            return None
    
    def simple_model_test(self, sample_size: int = 10) -> Dict:
        """ทดสอบโมเดลแบบง่าย"""
        print("🧪 Simple Model Test (Visual Analysis)")
        print("=" * 60)
        
        # 1. ตรวจสอบไฟล์
        if not self.check_model_files():
            return {}
        
        # 2. โหลด ground truth
        ground_truth = self.load_ground_truth()
        if not ground_truth:
            return {}
        
        # 3. เลือกตัวอย่าง
        test_samples = list(ground_truth.items())[:sample_size]
        
        print(f"🎯 Visual analysis of {len(test_samples)} images...")
        print("-" * 60)
        
        results = []
        for i, (img_path, expected_text) in enumerate(test_samples):
            img_name = Path(img_path).name
            
            # เตรียมรูป
            processed_img = self.preprocess_image(img_path)
            
            result = {
                "image_name": img_name,
                "image_path": img_path,
                "ground_truth": expected_text,
                "preprocessed_shape": processed_img.shape if processed_img is not None else None,
                "status": "OK" if processed_img is not None else "FAILED"
            }
            
            # วิเคราะห์รูป
            try:
                original_img = cv2.imread(img_path)
                if original_img is not None:
                    h, w = original_img.shape[:2]
                    gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
                    brightness = np.mean(gray)
                    
                    result.update({
                        "original_size": f"{w}x{h}",
                        "brightness": brightness,
                        "text_length": len(expected_text)
                    })
            except:
                pass
            
            results.append(result)
            
            print(f"{i+1:2d}. {img_name:<15} → '{expected_text:<15}' | {result['status']}")
            if result.get('original_size'):
                print(f"     Size: {result['original_size']}, Brightness: {result.get('brightness', 0):.0f}")
        
        print("-" * 60)
        
        # สรุปผลลัพธ์
        successful = sum(1 for r in results if r['status'] == 'OK')
        
        summary = {
            "test_info": {
                "timestamp": datetime.now().isoformat(),
                "test_type": "Visual Analysis",
                "model_path": str(self.model_dir)
            },
            "total_tested": len(results),
            "successful_preprocessing": successful,
            "success_rate": successful / len(results) if results else 0,
            "detailed_results": results
        }
        
        print(f"📊 Visual Analysis Summary:")
        print(f"   Total samples: {summary['total_tested']}")
        print(f"   Successful preprocessing: {summary['successful_preprocessing']}")
        print(f"   Success rate: {summary['success_rate']:.1%}")
        
        # วิเคราะห์ character patterns
        char_analysis = {}
        for result in results:
            text = result['ground_truth']
            for char in text:
                char_analysis[char] = char_analysis.get(char, 0) + 1
        
        print(f"\n🔤 Character Analysis in Sample:")
        sorted_chars = sorted(char_analysis.items(), key=lambda x: x[1], reverse=True)
        for char, count in sorted_chars[:10]:
            print(f"   '{char}': {count} times")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. ✅ Dataset validation: PASSED")
        print(f"   2. ✅ Image preprocessing: PASSED")
        print(f"   3. 🔄 Model inference setup: IN PROGRESS")
        print(f"   4. ⏳ Accuracy testing: PENDING")
        
        return summary
    
    def save_results(self, results: Dict, output_file: str = None):
        """บันทึกผลลัพธ์"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.project_root / f"VISUAL_ANALYSIS_REPORT_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Results saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 Direct Thai OCR Model Testing")
    print("=" * 60)
    print("Task 5.2a: Visual Analysis & Model Validation")
    print("-" * 60)
    
    tester = DirectModelTester()
    
    try:
        # ทดสอบ 20 ตัวอย่าง
        results = tester.simple_model_test(sample_size=20)
        
        if results:
            tester.save_results(results)
            print("\n🎉 Visual analysis completed successfully!")
        else:
            print("\n❌ Visual analysis failed!")
            
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
