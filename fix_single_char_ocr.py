#!/usr/bin/env python3
"""
🔧 Fix Single Character OCR Issues
แก้ปัญหาเฉพาะ Single Character Recognition
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SingleCharOCRFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def fix_issue_1_correct_config(self):
        """🔧 Issue 1: สร้าง config ที่ถูกต้องสำหรับ single character"""
        logger.info("🔧 แก้ปัญหา 1: สร้าง Single Character Config ที่ถูกต้อง")
        
        # สร้าง config ที่มั่นใจว่าเป็น single character
        correct_config = f"""Global:
  use_gpu: false
  pretrained_model: {self.project_root}/models/sagemaker_trained/best_accuracy
  character_dict_path: {self.project_root}/thai-letters/th_dict.txt
  character_type: thai
  max_text_length: 1
  infer_mode: true
  use_space_char: false
  save_res_path: ./inference_results.txt

Architecture:
  model_type: rec
  algorithm: CRNN
  Transform:
  Backbone:
    name: MobileNetV3
    scale: 0.5
    model_name: large
    disable_se: false
  Neck:
    name: SequenceEncoder
    encoder_type: rnn
    hidden_size: 96
  Head:
    name: CTCHead
    fc_decay: 0.00001

Loss:
  name: CTCLoss

PostProcess:
  name: CTCLabelDecode

Metric:
  name: RecMetric
  main_indicator: acc
"""
        
        config_path = self.project_root / "fixed_single_char_config.yml"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(correct_config)
            
        logger.info(f"✅ สร้าง Fixed Config: {config_path}")
        return config_path
    
    def fix_issue_2_test_paddleocr_version(self):
        """🔧 Issue 2: ตรวจสอบ PaddleOCR version และความเข้ากันได้"""
        logger.info("🔧 แก้ปัญหา 2: ตรวจสอบ PaddleOCR Version")
        
        # ตรวจสอบ PaddleOCR version
        try:
            cmd = ["python", "-c", "import paddleocr; print(f'PaddleOCR: {paddleocr.__version__}')"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.project_root))
            
            if result.returncode == 0:
                logger.info(f"✅ {result.stdout.strip()}")
            else:
                logger.warning(f"⚠️ ไม่สามารถตรวจสอบ PaddleOCR version: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"⚠️ Error checking PaddleOCR: {e}")
            
        # ตรวจสอบ model files
        model_files = [
            "best_accuracy.pdparams",
            "best_accuracy.pdopt", 
            "config.yml"
        ]
        
        model_dir = self.project_root / "models/sagemaker_trained"
        
        logger.info("🔍 ตรวจสอบไฟล์โมเดล:")
        for file in model_files:
            file_path = model_dir / file
            if file_path.exists():
                size = file_path.stat().st_size
                logger.info(f"  ✅ {file}: {size:,} bytes")
            else:
                logger.error(f"  ❌ {file}: ไม่พบไฟล์")
    
    def fix_issue_3_test_single_images(self, config_path):
        """🔧 Issue 3: ทดสอบกับภาพเดี่ยวๆ เพื่อดูปัญหา"""
        logger.info("🔧 แก้ปัญหา 3: ทดสอบกับภาพเดี่ยวๆ")
        
        # หาภาพทดสอบ
        test_images = []
        test_dirs = [
            self.project_root / "test_images",
            self.project_root / "thai-letters/datasets/converted/train_data_thai_paddleocr_0804_1144/train_data/rec/thai_data/val"
        ]
        
        for test_dir in test_dirs:
            if test_dir.exists():
                images = list(test_dir.glob("*.jpg"))[:3]
                test_images.extend(images)
                break
                
        if not test_images:
            logger.error("❌ ไม่พบภาพทดสอบ")
            return []
            
        logger.info(f"🧪 ทดสอบกับ {len(test_images)} ภาพ")
        
        results = []
        for img_path in test_images:
            logger.info(f"📷 ทดสอบ: {img_path.name}")
            
            # รัน inference
            cmd = [
                "python", "PaddleOCR/tools/infer_rec.py",
                "-c", os.path.relpath(config_path, self.project_root / "PaddleOCR"),
                "-o", f"Global.infer_img={os.path.relpath(img_path, self.project_root / 'PaddleOCR')}"
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root / "PaddleOCR"),
                    timeout=30
                )
                
                if result.returncode == 0 and "result:" in result.stdout:
                    # แยกผลลัพธ์
                    for line in result.stdout.split('\n'):
                        if "result:" in line:
                            predicted = line.split("result:")[1].strip()
                            
                            # ทำความสะอาดผลลัพธ์
                            if ' ' in predicted:
                                # แยก text และ confidence
                                parts = predicted.rsplit(' ', 1)
                                predicted_text = parts[0].strip()
                                try:
                                    confidence = float(parts[1])
                                except:
                                    confidence = 0.0
                            else:
                                predicted_text = predicted
                                confidence = 0.0
                            
                            # สำหรับ single character เอาแค่ตัวแรก
                            if predicted_text:
                                single_char = predicted_text[0]
                                
                                result_data = {
                                    "image": img_path.name,
                                    "raw_prediction": predicted,
                                    "predicted_text": predicted_text,
                                    "single_char": single_char,
                                    "confidence": confidence,
                                    "success": True
                                }
                                
                                results.append(result_data)
                                logger.info(f"  ✅ ผลลัพธ์: '{single_char}' (เต็ม: '{predicted_text}') | Conf: {confidence:.6f}")
                                break
                else:
                    error_data = {
                        "image": img_path.name,
                        "error": result.stderr if result.stderr else "No result found",
                        "stdout": result.stdout,
                        "success": False
                    }
                    results.append(error_data)
                    logger.warning(f"  ❌ ล้มเหลว: {error_data['error'][:50]}...")
                    
            except subprocess.TimeoutExpired:
                timeout_data = {
                    "image": img_path.name,
                    "error": "Timeout (30s)",
                    "success": False
                }
                results.append(timeout_data)
                logger.warning(f"  ⏱️ Timeout: {img_path.name}")
                
            except Exception as e:
                exception_data = {
                    "image": img_path.name,
                    "error": str(e),
                    "success": False
                }
                results.append(exception_data)
                logger.error(f"  ❌ Exception: {e}")
        
        return results
    
    def fix_issue_4_analyze_dictionary(self):
        """🔧 Issue 4: วิเคราะห์ dictionary และตัวอักษร"""
        logger.info("🔧 แก้ปัญหา 4: วิเคราะห์ Dictionary")
        
        dict_file = self.project_root / "thai-letters/th_dict.txt"
        
        if dict_file.exists():
            with open(dict_file, 'r', encoding='utf-8') as f:
                chars = f.read().strip().split('\n')
                
            logger.info(f"📖 Dictionary Analysis:")
            logger.info(f"  • จำนวนตัวอักษรทั้งหมด: {len(chars)}")
            
            # แยกประเภท
            thai_chars = [c for c in chars if '\u0e00' <= c <= '\u0e7f']
            english_chars = [c for c in chars if c.isalpha() and c.isascii()]
            numbers = [c for c in chars if c.isdigit()]
            symbols = [c for c in chars if not c.isalnum() and c.strip()]
            
            logger.info(f"  • ตัวอักษรไทย: {len(thai_chars)}")
            logger.info(f"  • ตัวอักษรอังกฤษ: {len(english_chars)}")
            logger.info(f"  • ตัวเลข: {len(numbers)}")
            logger.info(f"  • สัญลักษณ์: {len(symbols)}")
            
            # แสดงตัวอย่างตัวอักษรไทย
            if thai_chars:
                sample_thai = thai_chars[:20]
                logger.info(f"  • ตัวอย่างตัวอักษรไทย: {' '.join(sample_thai)}")
                
            return {
                "total": len(chars),
                "thai": len(thai_chars),
                "english": len(english_chars),
                "numbers": len(numbers),
                "symbols": len(symbols),
                "sample_thai": thai_chars[:20] if thai_chars else []
            }
        else:
            logger.error(f"❌ ไม่พบ dictionary: {dict_file}")
            return None
    
    def run_comprehensive_test(self):
        """🧪 รันการทดสอบแบบครบวงจร"""
        logger.info("🚀 เริ่มการแก้ปัญหาและทดสอบ Single Character OCR")
        
        # Fix Issue 1: Config
        config_path = self.fix_issue_1_correct_config()
        
        # Fix Issue 2: Version Check
        self.fix_issue_2_test_paddleocr_version()
        
        # Fix Issue 4: Dictionary Analysis
        dict_analysis = self.fix_issue_4_analyze_dictionary()
        
        # Fix Issue 3: Test with Single Images
        test_results = self.fix_issue_3_test_single_images(config_path)
        
        # สรุปผลลัพธ์
        successful_tests = [r for r in test_results if r.get("success", False)]
        failed_tests = [r for r in test_results if not r.get("success", False)]
        
        summary = {
            "timestamp": self.timestamp,
            "config_path": str(config_path),
            "dictionary_analysis": dict_analysis,
            "test_results": {
                "total": len(test_results),
                "successful": len(successful_tests),
                "failed": len(failed_tests),
                "success_rate": len(successful_tests) / len(test_results) if test_results else 0
            },
            "detailed_results": test_results
        }
        
        # บันทึกผลลัพธ์
        results_file = self.project_root / f"single_char_fix_results_{self.timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        # แสดงสรุป
        print(f"\n{'='*60}")
        print(f"🎯 สรุปการแก้ปัญหา Single Character OCR")
        print(f"{'='*60}")
        print(f"📊 ผลการทดสอบ:")
        print(f"  • ทดสอบทั้งหมด: {summary['test_results']['total']}")
        print(f"  • สำเร็จ: {summary['test_results']['successful']}")
        print(f"  • ล้มเหลว: {summary['test_results']['failed']}")
        print(f"  • อัตราความสำเร็จ: {summary['test_results']['success_rate']:.1%}")
        
        if successful_tests:
            print(f"\n✅ ตัวอย่างผลลัพธ์ที่สำเร็จ:")
            for result in successful_tests[:5]:
                print(f"  📷 {result['image']}: '{result['single_char']}' (conf: {result['confidence']:.6f})")
        
        if failed_tests:
            print(f"\n❌ ปัญหาที่พบ:")
            error_types = {}
            for result in failed_tests:
                error = result.get('error', 'Unknown')[:30]
                error_types[error] = error_types.get(error, 0) + 1
            
            for error, count in error_types.items():
                print(f"  • {error}: {count} ครั้ง")
        
        print(f"\n📄 รายงานละเอียด: {results_file}")
        print(f"⚙️ Config ที่แก้ไข: {config_path}")
        
        return summary

def main():
    fixer = SingleCharOCRFixer()
    result = fixer.run_comprehensive_test()
    
    print(f"\n🎯 สถานะ: {'✅ สำเร็จ' if result['test_results']['success_rate'] > 0 else '❌ ต้องแก้ไขเพิ่มเติม'}")

if __name__ == "__main__":
    main()
