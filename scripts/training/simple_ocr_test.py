#!/usr/bin/env python3
"""
Simple Model Testing with Real Images
ทดสอบโมเดลแบบง่ายๆ กับรูปภาพจริง
"""

import os
import sys
import logging
import json
from pathlib import Path

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
                        validation_data.append({
                            'image_path': full_image_path,
                            'relative_path': image_path,
                            'true_label': true_label,
                            'line_num': line_num
                        })
    
    logger.info(f"✅ Found {len(validation_data)} validation samples")
    return validation_data

def test_with_basic_paddleocr():
    """ทดสอบด้วย PaddleOCR basic"""
    
    try:
        logger.info("🔧 Initializing PaddleOCR...")
        
        # เพิ่ม PaddleOCR ใน path
        sys.path.append('PaddleOCR')
        from paddleocr import PaddleOCR
        
        # Initialize PaddleOCR สำหรับตัวเลข
        ocr = PaddleOCR(
            use_angle_cls=False,
            lang='en',  # ใช้ English สำหรับตัวเลข
            show_log=False,
            use_gpu=False
        )
        
        logger.info("✅ PaddleOCR initialized successfully")
        return ocr
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize PaddleOCR: {str(e)}")
        return None

def test_custom_model():
    """ทดสอบด้วยโมเดลที่เทรนเอง (ถ้าเป็นไปได้)"""
    
    try:
        logger.info("🔧 Trying to load custom trained model...")
        
        # ตรวจสอบโมเดลที่เทรนแล้ว
        model_files = [
            "models/sagemaker_trained/best_model/inference.pdmodel",
            "models/sagemaker_trained/best_model/inference.pdiparams",
            "models/sagemaker_trained/best_accuracy.pdparams"
        ]
        
        for model_file in model_files:
            if os.path.exists(model_file):
                logger.info(f"   ✅ Found: {model_file}")
            else:
                logger.warning(f"   ❌ Missing: {model_file}")
        
        # ลองใช้ PaddleOCR กับโมเดลที่เทรนเอง
        sys.path.append('PaddleOCR')
        from paddleocr import PaddleOCR
        
        # ลองใช้ path ที่มีโมเดลที่เทรนแล้ว
        if os.path.exists("models/sagemaker_trained/best_model/"):
            ocr = PaddleOCR(
                det_model_dir=None,  # ไม่ใช้ detection
                rec_model_dir="models/sagemaker_trained/best_model/",
                use_angle_cls=False,
                lang='th',
                show_log=False,
                use_gpu=False
            )
            logger.info("✅ Custom model loaded successfully")
            return ocr
        else:
            logger.warning("⚠️ Custom model path not found")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to load custom model: {str(e)}")
        return None

def test_images_with_ocr(ocr, validation_data, max_samples=10):
    """ทดสอบรูปภาพด้วย OCR"""
    
    if not ocr:
        logger.error("❌ No OCR instance available")
        return []
    
    test_samples = validation_data[:max_samples]
    results = []
    
    logger.info(f"🧪 Testing {len(test_samples)} images...")
    logger.info("-" * 60)
    
    for i, sample in enumerate(test_samples, 1):
        image_path = sample['image_path']
        true_label = sample['true_label']
        
        logger.info(f"[{i}/{len(test_samples)}] Testing: {os.path.basename(image_path)}")
        logger.info(f"   Expected: '{true_label}'")
        
        try:
            # รัน OCR
            result = ocr.ocr(image_path, cls=False)
            
            if result and result[0]:
                # แยกข้อความและ confidence
                predictions = []
                confidences = []
                
                for line in result[0]:
                    if len(line) >= 2:
                        text = line[1][0]
                        conf = line[1][1]
                        predictions.append(text)
                        confidences.append(conf)
                
                predicted_text = " ".join(predictions) if predictions else ""
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                
                # เปรียบเทียบผลลัพธ์
                is_correct = predicted_text.strip() == true_label.strip()
                
                if is_correct:
                    logger.info(f"   ✅ Predicted: '{predicted_text}' (confidence: {avg_confidence:.3f}) - CORRECT!")
                else:
                    logger.info(f"   ❌ Predicted: '{predicted_text}' (confidence: {avg_confidence:.3f}) - INCORRECT")
                
                results.append({
                    'image': os.path.basename(image_path),
                    'true_label': true_label,
                    'predicted_text': predicted_text,
                    'confidence': avg_confidence,
                    'correct': is_correct
                })
            else:
                logger.info(f"   ⚠️ No text detected")
                results.append({
                    'image': os.path.basename(image_path),
                    'true_label': true_label,
                    'predicted_text': "",
                    'confidence': 0.0,
                    'correct': False
                })
                
        except Exception as e:
            logger.error(f"   ❌ Error processing image: {str(e)}")
            results.append({
                'image': os.path.basename(image_path),
                'true_label': true_label,
                'predicted_text': None,
                'confidence': 0.0,
                'correct': False
            })
        
        logger.info("")
    
    return results

def main():
    """Main function"""
    
    logger.info("🎯 Simple Model Testing with Real Images")
    logger.info("=" * 60)
    
    # อ่านข้อมูล validation
    validation_data = read_validation_data()
    
    if not validation_data:
        logger.error("❌ No validation data found")
        return 1
    
    # แสดงตัวอย่างข้อมูล
    logger.info("📋 Sample validation data:")
    for i, sample in enumerate(validation_data[:5], 1):
        logger.info(f"   [{i}] {sample['relative_path']} → '{sample['true_label']}'")
    logger.info(f"   ... and {len(validation_data) - 5} more samples")
    logger.info("")
    
    # ลองทดสอบด้วยโมเดลที่เทรนเอง
    logger.info("🔬 Attempting to test with custom trained model...")
    custom_ocr = test_custom_model()
    
    if custom_ocr:
        logger.info("✅ Testing with custom trained model")
        results = test_images_with_ocr(custom_ocr, validation_data, max_samples=10)
    else:
        # ถ้าโมเดลที่เทรนเองไม่ได้ ให้ใช้ PaddleOCR basic
        logger.info("🔬 Falling back to basic PaddleOCR...")
        basic_ocr = test_with_basic_paddleocr()
        
        if basic_ocr:
            logger.info("✅ Testing with basic PaddleOCR")
            results = test_images_with_ocr(basic_ocr, validation_data, max_samples=10)
        else:
            logger.error("❌ Failed to initialize any OCR system")
            return 1
    
    # สรุปผลลัพธ์
    if results:
        correct_count = sum(1 for r in results if r['correct'])
        total_count = len(results)
        accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
        
        logger.info("=" * 60)
        logger.info("📊 SUMMARY")
        logger.info(f"📊 Total tested: {total_count}")
        logger.info(f"✅ Correct predictions: {correct_count}")
        logger.info(f"🎯 Accuracy: {accuracy:.1f}%")
        
        # บันทึกผลลัพธ์
        results_file = "simple_ocr_test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_tested': total_count,
                    'correct_predictions': correct_count,
                    'accuracy': accuracy,
                    'test_date': '2025-08-07'
                },
                'results': results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Results saved to: {results_file}")
    
    logger.info("✅ Testing completed!")
    return 0

if __name__ == '__main__':
    exit(main())
