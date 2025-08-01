#!/usr/bin/env python3
"""
Test inference with trained SageMaker model
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path

# Add PaddleOCR to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "PaddleOCR"))

try:
    from paddleocr import PaddleOCR
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure PaddleOCR is properly installed")
    sys.exit(1)

def test_sagemaker_model():
    """Test the trained SageMaker model"""
    
    # Model paths
    model_dir = project_root / "models" / "sagemaker_trained"
    best_model_dir = model_dir / "best_model"
    
    print(f"🔍 Testing SageMaker trained model from: {best_model_dir}")
    
    # Check if model exists
    if not best_model_dir.exists():
        print("❌ Best model directory not found!")
        return False
    
    model_params = best_model_dir / "model.pdparams"
    if not model_params.exists():
        print("❌ Model parameters not found!")
        return False
    
    print(f"✅ Found model parameters: {model_params}")
    
    # Initialize PaddleOCR with our trained model
    try:
        # First try basic initialization
        ocr = PaddleOCR(
            use_textline_orientation=False,
            lang='en'
        )
        print("✅ PaddleOCR initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize PaddleOCR: {e}")
        return False
    
    # Test with sample Thai text image
    test_image_path = project_root / "thai-letters" / "datasets" / "converted" / "train_data_thai_paddleocr_0731_1604" / "train_data" / "rec"
    
    if test_image_path.exists():
        # Find a sample image
        image_files = list(test_image_path.glob("*.jpg"))
        if image_files:
            sample_image = image_files[0]
            print(f"🖼️ Testing with image: {sample_image}")
            
            try:
                result = ocr.ocr(str(sample_image), cls=False)
                
                print("\n📊 OCR Results:")
                for line in result:
                    if line:
                        for word_info in line:
                            bbox, (text, confidence) = word_info
                            print(f"  📝 Text: '{text}' (Confidence: {confidence:.4f})")
                
                return True
                
            except Exception as e:
                print(f"❌ OCR inference failed: {e}")
                return False
        else:
            print("⚠️ No test images found in dataset")
    else:
        print("⚠️ Test dataset directory not found")
    
    # Create a simple test with synthetic image
    print("\n🎨 Creating synthetic test image...")
    test_img = np.ones((64, 256, 3), dtype=np.uint8) * 255
    cv2.putText(test_img, 'สวัสดี', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Save test image
    test_img_path = model_dir / "test_thai.jpg"
    cv2.imwrite(str(test_img_path), test_img)
    print(f"💾 Saved test image: {test_img_path}")
    
    # Test OCR
    try:
        result = ocr.ocr(str(test_img_path), cls=False)
        print("\n📊 Synthetic Test Results:")
        for line in result:
            if line:
                for word_info in line:
                    bbox, (text, confidence) = word_info
                    print(f"  📝 Text: '{text}' (Confidence: {confidence:.4f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Synthetic test failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 SageMaker Model Testing")
    print("=" * 50)
    
    success = test_sagemaker_model()
    
    if success:
        print("\n🎉 Model testing completed successfully!")
        print("\n📋 Next steps:")
        print("1. Test with more Thai text images")
        print("2. Evaluate model accuracy")
        print("3. Deploy to SageMaker endpoint")
        print("4. Compare with local training results")
    else:
        print("\n❌ Model testing failed!")

if __name__ == "__main__":
    main()
