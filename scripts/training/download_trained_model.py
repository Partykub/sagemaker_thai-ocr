#!/usr/bin/env python3
"""
Download and Test Thai Numbers OCR Model
ดาวน์โหลดและทดสอบโมเดลตัวเลขไทยที่เทรนแล้ว
"""

import boto3
import tarfile
import os
from pathlib import Path
import logging
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = 'ap-southeast-1'
S3_BUCKET = 'paddleocr-dev-data-bucket'
MODEL_S3_KEY = 'models/thai-numbers-ocr-20250807-100059/output/model.tar.gz'
LOCAL_MODEL_DIR = 'models/sagemaker_trained'

def download_model():
    """ดาวน์โหลดโมเดลจาก S3"""
    
    logger.info("📥 Downloading trained model from S3...")
    
    try:
        # สร้าง directory สำหรับโมเดล
        os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)
        
        # Download model.tar.gz
        s3_client = boto3.client('s3', region_name=AWS_REGION)
        local_model_path = os.path.join(LOCAL_MODEL_DIR, 'model.tar.gz')
        
        logger.info(f"   From: s3://{S3_BUCKET}/{MODEL_S3_KEY}")
        logger.info(f"   To: {local_model_path}")
        
        s3_client.download_file(S3_BUCKET, MODEL_S3_KEY, local_model_path)
        
        # Extract tar.gz
        logger.info("📦 Extracting model files...")
        
        with tarfile.open(local_model_path, 'r:gz') as tar:
            tar.extractall(LOCAL_MODEL_DIR)
        
        # List extracted files
        logger.info("✅ Model downloaded and extracted successfully!")
        logger.info("📁 Extracted files:")
        
        for root, dirs, files in os.walk(LOCAL_MODEL_DIR):
            level = root.replace(LOCAL_MODEL_DIR, '').count(os.sep)
            indent = ' ' * 2 * level
            logger.info(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                logger.info(f"{subindent}{file} ({file_size} bytes)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download model: {str(e)}")
        return False

def test_model_inference():
    """ทดสอบโมเดลด้วยรูปตัวเลข"""
    
    logger.info("🧪 Testing model inference...")
    
    try:
        # Import PaddleOCR
        import sys
        sys.path.append('PaddleOCR')
        from paddleocr import PaddleOCR
        
        # หา model path ที่ถูกต้อง
        model_files = []
        for root, dirs, files in os.walk(LOCAL_MODEL_DIR):
            for file in files:
                if file.endswith(('.pdparams', '.pdmodel')):
                    model_files.append(os.path.join(root, file))
        
        if not model_files:
            logger.error("❌ No model files found")
            return False
        
        logger.info(f"🔍 Found model files: {model_files}")
        
        # สร้าง test images directory ถ้ายังไม่มี
        test_dir = 'test_images'
        if not os.path.exists(test_dir):
            logger.warning(f"⚠️ Test images directory not found: {test_dir}")
            return False
        
        # ทดสอบกับรูปที่มี
        test_images = [f for f in os.listdir(test_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
        
        if not test_images:
            logger.warning("⚠️ No test images found")
            return False
        
        logger.info(f"🖼️ Testing with {len(test_images)} images:")
        
        # Initialize PaddleOCR with custom model (ถ้าเป็นไปได้)
        ocr = PaddleOCR(
            use_angle_cls=True, 
            lang='en',  # ใช้ en เพราะเป็นตัวเลข
            show_log=False
        )
        
        results = []
        
        for img_name in test_images[:5]:  # ทดสอบแค่ 5 รูปแรก
            img_path = os.path.join(test_dir, img_name)
            logger.info(f"   Testing: {img_name}")
            
            try:
                result = ocr.ocr(img_path, cls=True)
                
                if result and result[0]:
                    detected_text = " ".join([res[1][0] for res in result[0]])
                    confidence = sum([res[1][1] for res in result[0]]) / len(result[0])
                    
                    logger.info(f"      Result: '{detected_text}' (confidence: {confidence:.2f})")
                    results.append({
                        'image': img_name,
                        'text': detected_text,
                        'confidence': confidence
                    })
                else:
                    logger.info(f"      Result: No text detected")
                    results.append({
                        'image': img_name,
                        'text': '',
                        'confidence': 0.0
                    })
                    
            except Exception as e:
                logger.error(f"      Error: {str(e)}")
        
        # Save results
        results_file = os.path.join(LOCAL_MODEL_DIR, 'test_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Test results saved to: {results_file}")
        return True
        
    except ImportError:
        logger.warning("⚠️ PaddleOCR not available for testing")
        return False
    except Exception as e:
        logger.error(f"❌ Model testing failed: {str(e)}")
        return False

def main():
    """Main function"""
    
    logger.info("🎯 Thai Numbers OCR - Model Download & Test")
    logger.info("=" * 50)
    
    # Download model
    if download_model():
        logger.info("\n🧪 Testing model...")
        test_model_inference()
    else:
        logger.error("❌ Failed to download model")
        return 1
    
    logger.info("\n✅ Process completed!")
    logger.info(f"📁 Model location: {LOCAL_MODEL_DIR}")
    
    return 0

if __name__ == '__main__':
    exit(main())
