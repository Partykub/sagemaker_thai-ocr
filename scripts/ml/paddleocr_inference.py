#!/usr/bin/env python3
"""
PaddleOCR Inference Tools: ใช้ PaddleOCR tools เพื่อ inference กับโมเดลที่เทรนมา
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
import json
import random
from typing import Dict, List, Tuple

# Add PaddleOCR paths
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "PaddleOCR"))
sys.path.append(str(project_root / "PaddleOCR" / "tools"))

try:
    import paddle
    from tools.infer_rec import TextRecognizer
    from ppocr.utils.utility import get_model_config
    print("✅ PaddleOCR tools imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class PaddleOCRInference:
    """ใช้ PaddleOCR tools สำหรับ inference กับโมเดลที่เทรนมา"""
    
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.project_root = project_root
        self.text_recognizer = None
        
    def initialize_recognizer(self) -> bool:
        """เริ่มต้น Text Recognizer"""
        try:
            print("🤖 Initializing PaddleOCR Text Recognizer...")
            
            # ตั้งค่า arguments สำหรับ TextRecognizer
            class Args:
                def __init__(self, model_dir: Path):
                    # Model paths
                    self.rec_model_dir = str(model_dir / "best_model")  # ใช้ best_model directory
                    self.rec_image_shape = "3, 64, 256"  # ขนาดรูปที่โมเดลคาดหวัง
                    self.rec_batch_num = 1
                    self.max_text_length = 25
                    
                    # Character dictionary
                    dict_file = project_root / "th_dict.txt"
                    self.rec_char_dict_path = str(dict_file) if dict_file.exists() else None
                    
                    # Algorithm และ settings
                    self.rec_algorithm = "CRNN"
                    self.use_space_char = False
                    
                    # Hardware settings
                    self.use_gpu = False  # ใช้ CPU
                    self.use_tensorrt = False
                    self.use_fp16 = False
                    self.gpu_mem = 500
                    
                    # Output settings
                    self.vis_font_path = None
                    self.drop_score = 0.5
            
            args = Args(self.model_dir)
            
            print(f"📁 Model directory: {args.rec_model_dir}")
            print(f"📄 Character dict: {args.rec_char_dict_path}")
            
            # ตรวจสอบว่า model directory มีอยู่จริง
            model_path = Path(args.rec_model_dir)
            if not model_path.exists():
                print(f"❌ Model directory not found: {model_path}")
                return False
            
            # ตรวจสอบไฟล์ในโฟลเดอร์
            model_files = list(model_path.iterdir())
            print(f"📊 Model files: {[f.name for f in model_files]}")
            
            # สร้าง TextRecognizer
            self.text_recognizer = TextRecognizer(args)
            
            print("✅ Text Recognizer initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Text Recognizer: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def recognize_image(self, img_path: str) -> Tuple[str, float]:
        """ทำ OCR กับรูปภาพ"""
        try:
            if self.text_recognizer is None:
                print("❌ Text Recognizer not initialized")
                return "", 0.0
            
            # อ่านรูป
            img = cv2.imread(img_path)
            if img is None:
                print(f"❌ Cannot read image: {img_path}")
                return "", 0.0
            
            # ใช้ TextRecognizer
            img_list = [img]
            rec_res, elapse = self.text_recognizer(img_list)
            
            # Extract ผลลัพธ์
            if rec_res and len(rec_res) > 0:
                text = rec_res[0][0]  # ข้อความ
                confidence = rec_res[0][1]  # confidence
                return text, confidence
            else:
                return "", 0.0
            
        except Exception as e:
            print(f"❌ Recognition error: {e}")
            return "", 0.0

def test_paddleocr_inference():
    """ทดสอบ PaddleOCR inference"""
    print("🧪 Testing PaddleOCR Inference with Trained Model")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent.parent
    model_dir = project_root / "models" / "sagemaker_trained"
    
    # สร้าง inference engine
    inference = PaddleOCRInference(model_dir)
    
    # เริ่มต้น recognizer
    if not inference.initialize_recognizer():
        print("❌ Failed to initialize recognizer")
        return False
    
    # ทดสอบกับรูปตัวอย่าง
    dataset_dir = project_root / "thai-letters" / "datasets" / "converted" / "train_data_thai_paddleocr_0731_1604"
    val_images_dir = dataset_dir / "train_data" / "rec" / "thai_data" / "val"
    val_labels_file = dataset_dir / "train_data" / "rec" / "rec_gt_val.txt"
    
    if not val_images_dir.exists() or not val_labels_file.exists():
        print("❌ Validation data not found")
        return False
    
    # โหลด ground truth
    ground_truth = {}
    with open(val_labels_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '\t' in line:
                img_path, text_label = line.split('\t', 1)
                full_path = dataset_dir / "train_data" / "rec" / img_path
                if full_path.exists():
                    ground_truth[str(full_path)] = text_label
    
    # เลือกตัวอย่าง 10 รูป
    test_samples = list(ground_truth.items())[:10]
    
    print(f"\n🎯 Testing with {len(test_samples)} sample images:")
    print("-" * 60)
    
    correct_count = 0
    total_confidence = 0.0
    
    for i, (img_path, expected_text) in enumerate(test_samples, 1):
        img_name = Path(img_path).name
        print(f"\n📷 Test {i}: {img_name}")
        print(f"✅ Expected: '{expected_text}'")
        
        # ทำ OCR
        predicted_text, confidence = inference.recognize_image(img_path)
        total_confidence += confidence
        
        print(f"🤖 Predicted: '{predicted_text}'")
        print(f"📊 Confidence: {confidence:.4f}")
        
        # เปรียบเทียบ
        is_correct = predicted_text.strip() == expected_text.strip()
        if is_correct:
            correct_count += 1
            print(f"✅ Result: CORRECT")
        else:
            print(f"❌ Result: INCORRECT")
    
    # สรุปผลลัพธ์
    accuracy = correct_count / len(test_samples) if test_samples else 0
    avg_confidence = total_confidence / len(test_samples) if test_samples else 0
    
    print(f"\n" + "=" * 60)
    print(f"📊 INFERENCE TEST SUMMARY")
    print(f"=" * 60)
    print(f"🎯 Total samples: {len(test_samples)}")
    print(f"✅ Correct predictions: {correct_count}")
    print(f"📈 Accuracy: {accuracy:.2%}")
    print(f"🔮 Average confidence: {avg_confidence:.4f}")
    
    if accuracy > 0.7:
        print(f"🎉 Excellent! Model is working well")
    elif accuracy > 0.5:
        print(f"👍 Good! Model shows promising results")
    elif accuracy > 0.3:
        print(f"⚠️ Moderate performance, needs improvement")
    else:
        print(f"❌ Poor performance, model may need retraining")
    
    print(f"\n✅ PaddleOCR inference test completed!")
    return True

if __name__ == "__main__":
    test_paddleocr_inference()
