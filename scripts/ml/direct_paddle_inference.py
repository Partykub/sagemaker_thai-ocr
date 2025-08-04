#!/usr/bin/env python3
"""
Direct Paddle Inference: ใช้โมเดลที่เทรนมาโดยตรงผ่าน Paddle inference API
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
import paddle
from typing import Tuple, List

# Add PaddleOCR path for utilities
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "PaddleOCR"))

class DirectPaddleInference:
    """ใช้โมเดลที่เทรนมาผ่าน Paddle inference โดยตรง"""
    
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.model_path = model_dir / "best_model" / "model"  # ใช้ best_model/model.pdparams
        self.predictor = None
        self.char_dict = None
        
    def load_character_dict(self) -> bool:
        """โหลด character dictionary"""
        # หาไฟล์ dict
        dict_files = [
            self.model_dir.parent.parent / "th_dict.txt",
            self.model_dir.parent.parent / "PaddleOCR" / "ppocr" / "utils" / "dict" / "th_dict.txt",
            self.model_dir.parent.parent / "thai-letters" / "th_dict.txt"
        ]
        
        for dict_file in dict_files:
            if dict_file.exists():
                try:
                    with open(dict_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        self.char_dict = ['blank'] + [line.strip() for line in lines if line.strip()]
                    print(f"✅ Loaded character dictionary: {len(self.char_dict)} characters from {dict_file.name}")
                    return True
                except Exception as e:
                    print(f"⚠️ Error loading {dict_file}: {e}")
                    continue
        
        # สร้าง basic dict ถ้าหาไม่เจอ
        self._create_basic_thai_dict()
        return True
    
    def _create_basic_thai_dict(self):
        """สร้าง character dictionary พื้นฐาน"""
        thai_chars = [
            # พยัญชนะ
            'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ',
            'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ',
            'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ษ',
            'ส', 'ห', 'ฬ', 'อ', 'ฮ',
            # สระและวรรณยุกต์
            'ะ', 'ั', 'า', 'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'เ', 'แ', 'โ',
            'ใ', 'ไ', 'ๅ', 'ๆ', '็', '่', '้', '๊', '๋', '์',
            # ตัวเลข
            '๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙',
            # พิเศษ
            'ฯ', '๏', '๚', '๛', ' '
        ]
        
        self.char_dict = ['blank'] + thai_chars
        print(f"✅ Created basic Thai dictionary: {len(self.char_dict)} characters")
    
    def initialize_inference(self) -> bool:
        """เริ่มต้น Paddle inference"""
        try:
            # ใช้ best_model/model.pdparams และ model.pdmodel
            model_file = str(self.model_path) + ".pdmodel"
            param_file = str(self.model_path) + ".pdparams"
            
            print(f"🔍 Looking for model files:")
            print(f"   Model: {model_file}")
            print(f"   Params: {param_file}")
            
            # ตรวจสอบไฟล์
            if not Path(model_file).exists():
                print(f"❌ Model file not found: {model_file}")
                return False
            
            if not Path(param_file).exists():
                print(f"❌ Params file not found: {param_file}")
            
            # ตั้งค่า inference config
            config = paddle.inference.Config()
            config.set_model(model_file, param_file)
            print(f"✅ Using model files: {Path(model_file).name}, {Path(param_file).name}")
            
            # ตั้งค่าการใช้งาน
            config.disable_gpu()  # ใช้ CPU
            config.set_cpu_math_library_num_threads(4)
            config.switch_use_feed_fetch_ops(False)
            config.switch_specify_input_names(True)
            
            # สร้าง predictor
            self.predictor = paddle.inference.create_predictor(config)
            print("✅ Paddle inference initialized successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize inference: {e}")
            return False
            
            print("✅ Paddle inference initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Paddle inference: {e}")
            return False
    
    def preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """เตรียมรูปภาพสำหรับ inference"""
        try:
            # แปลงเป็น grayscale ถ้าจำเป็น
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Resize ตามขนาดที่โมเดลคาดหวัง (32x128 สำหรับ recognition)
            target_height = 32
            target_width = 128
            
            img_resized = cv2.resize(img, (target_width, target_height))
            
            # Normalize เป็น [0, 1]
            img_normalized = img_resized.astype(np.float32) / 255.0
            
            # เพิ่ม channel dimension และ batch dimension
            img_final = np.expand_dims(img_normalized, axis=0)  # (1, 32, 128)
            img_final = np.expand_dims(img_final, axis=0)      # (1, 1, 32, 128)
            
            return img_final
            
        except Exception as e:
            print(f"❌ Error preprocessing image: {e}")
            return None
    
    def run_inference(self, img: np.ndarray) -> Tuple[str, float]:
        """รัน inference กับรูปภาพ"""
        try:
            if self.predictor is None:
                return "", 0.0
            
            # เตรียมรูป
            processed_img = self.preprocess_image(img)
            if processed_img is None:
                return "", 0.0
            
            # ตั้งค่า input
            input_names = self.predictor.get_input_names()
            input_tensor = self.predictor.get_input_handle(input_names[0])
            input_tensor.reshape(processed_img.shape)
            input_tensor.copy_from_cpu(processed_img)
            
            # รัน inference
            self.predictor.run()
            
            # ดึงผลลัพธ์
            output_names = self.predictor.get_output_names()
            output_tensor = self.predictor.get_output_handle(output_names[0])
            output_data = output_tensor.copy_to_cpu()
            
            # แปลงผลลัพธ์เป็นข้อความ
            text, confidence = self._decode_output(output_data)
            
            return text, confidence
            
        except Exception as e:
            print(f"❌ Inference error: {e}")
            return "", 0.0
    
    def _decode_output(self, output_data: np.ndarray) -> Tuple[str, float]:
        """แปลง output เป็นข้อความ"""
        try:
            # CTC decoding
            if len(output_data.shape) == 3:
                output_data = output_data[0]  # remove batch dimension
            
            # Argmax เพื่อหา character indices
            indices = np.argmax(output_data, axis=1)
            
            # CTC decoding - remove blanks and duplicates
            decoded_chars = []
            prev_char = -1
            
            for idx in indices:
                if idx != 0 and idx != prev_char:  # 0 is blank
                    if idx < len(self.char_dict):
                        decoded_chars.append(self.char_dict[idx])
                prev_char = idx
            
            text = ''.join(decoded_chars)
            
            # คำนวณ confidence (average of max probabilities)
            max_probs = np.max(output_data, axis=1)
            confidence = np.mean(max_probs)
            
            return text, float(confidence)
            
        except Exception as e:
            print(f"❌ Decoding error: {e}")
            return "", 0.0

def test_direct_inference():
    """ทดสอบ direct inference"""
    print("🧪 Testing Direct Paddle Inference")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent.parent
    model_dir = project_root / "models" / "sagemaker_trained"
    
    # สร้าง inference engine
    inference = DirectPaddleInference(model_dir)
    
    # โหลด character dictionary
    if not inference.load_character_dict():
        print("❌ Failed to load character dictionary")
        return False
    
    # เริ่มต้น inference
    if not inference.initialize_inference():
        print("❌ Failed to initialize inference")
        return False
    
    # ทดสอบกับรูปตัวอย่าง
    test_img_dir = project_root / "thai-letters" / "datasets" / "converted" / "train_data_thai_paddleocr_0731_1604" / "train_data" / "rec" / "thai_data" / "val"
    
    if test_img_dir.exists():
        test_images = list(test_img_dir.glob("*.jpg"))[:5]  # ทดสอบ 5 รูปแรก
        
        print(f"\n🎯 Testing with {len(test_images)} sample images:")
        
        for i, img_path in enumerate(test_images, 1):
            print(f"\n📷 Test {i}: {img_path.name}")
            
            # อ่านรูป
            img = cv2.imread(str(img_path))
            if img is None:
                print("❌ Cannot read image")
                continue
            
            # รัน inference
            text, confidence = inference.run_inference(img)
            print(f"   Result: '{text}' (confidence: {confidence:.4f})")
    
    print("\n✅ Direct inference test completed!")
    return True

if __name__ == "__main__":
    test_direct_inference()
