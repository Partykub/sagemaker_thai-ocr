#!/usr/bin/env python3
"""
Test the numbers model with proper validation dataset
Uses the numbers validation data (0-9) instead of Thai characters
"""

import os
import sys
import subprocess
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NumbersModelTester:
    """Test the numbers model with correct validation dataset"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.paddleocr_dir = self.project_root / "PaddleOCR"
        self.model_dir = self.project_root / "models" / "sagemaker_trained"
        
        # Use the CORRECT validation data for numbers (0-9)
        self.validation_file = self.project_root / "thai-letters" / "datasets" / "converted" / "train_data_thai_paddleocr_0806_1433" / "train_data" / "rec" / "rec_gt_val.txt"
        self.validation_images_dir = self.project_root / "thai-letters" / "datasets" / "converted" / "train_data_thai_paddleocr_0806_1433" / "train_data" / "rec"
        
        # Numbers dictionary (0-9 only)
        self.numbers_dict_file = self.project_root / "numbers_dict.txt"
        
        self.config_file = self.project_root / "numbers_inference_config.yml"
        
    def create_numbers_dictionary(self):
        """Create a simple numbers dictionary for 0-9"""
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        
        with open(self.numbers_dict_file, 'w', encoding='utf-8') as f:
            for num in numbers:
                f.write(num + '\n')
                
        logger.info(f"✅ Created numbers dictionary: {self.numbers_dict_file}")
        return self.numbers_dict_file
        
    def create_inference_config(self):
        """Create inference configuration for numbers model"""
        config_content = f"""Global:
  use_gpu: false
  epoch_num: 100
  log_smooth_window: 20
  print_batch_step: 10
  save_model_dir: ./output/rec/
  save_epoch_step: 10
  eval_batch_step: 500
  cal_metric_during_train: true
  pretrained_model: {self.model_dir}/best_accuracy
  character_dict_path: {self.numbers_dict_file}
  character_type: EN  # English/Numbers
  max_text_length: 1  # Single character
  infer_mode: true
  use_space_char: false
  save_res_path: ./numbers_inference_results.txt

Architecture:
  model_type: rec
  algorithm: CRNN
  Transform:
  Backbone:
    name: MobileNetV3
    scale: 0.5
    model_name: large
    small_stride: [1, 2, 2, 2]
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

Train:
  dataset:
    name: SimpleDataSet
    data_dir: ./train_data/rec/
    label_file_list:
    - ./train_data/rec/rec_gt_train.txt
    transforms:
    - DecodeImage:
        img_mode: BGR
        channel_first: false
    - RecAug:
    - CTCLabelEncode:
    - RecResizeImg:
        image_shape: [3, 32, 128]
    - KeepKeys:
        keep_keys:
        - image
        - label
        - length
  loader:
    shuffle: true
    batch_size_per_card: 64
    drop_last: true
    num_workers: 4

Eval:
  dataset:
    name: SimpleDataSet
    data_dir: ./train_data/rec/
    label_file_list:
    - ./train_data/rec/rec_gt_val.txt
    transforms:
    - DecodeImage:
        img_mode: BGR
        channel_first: false
    - CTCLabelEncode:
    - RecResizeImg:
        image_shape: [3, 32, 128]
    - KeepKeys:
        keep_keys:
        - image
        - label
        - length
  loader:
    shuffle: false
    drop_last: false
    batch_size_per_card: 64
    num_workers: 4
"""
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
            
        logger.info(f"✅ Created inference config: {self.config_file}")
        
    def load_validation_data(self, max_samples: int = 15) -> List[Tuple[str, str]]:
        """Load validation data with numbers (0-9)"""
        validation_data = []
        
        if not self.validation_file.exists():
            logger.error(f"❌ Validation file not found: {self.validation_file}")
            return validation_data
            
        logger.info(f"📖 Loading validation data from: {self.validation_file}")
        
        with open(self.validation_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= max_samples:
                    break
                    
                line = line.strip()
                if '\t' in line:
                    img_path, label = line.split('\t', 1)
                    validation_data.append((img_path, label))
                    
        logger.info(f"✅ Loaded {len(validation_data)} validation samples")
        return validation_data
        
    def test_single_image(self, image_path: str) -> Tuple[str, float]:
        """Test a single image with the numbers model"""
        full_image_path = self.validation_images_dir / image_path
        
        if not full_image_path.exists():
            logger.error(f"❌ Image not found: {full_image_path}")
            return "", 0.0
            
        # Run PaddleOCR inference
        cmd = [
            "python", str(self.paddleocr_dir / "tools" / "infer_rec.py"),
            "-c", str(self.config_file),
            "-o", f"Global.infer_img={full_image_path}"
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=str(self.paddleocr_dir),
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse output: "result: 5 0.9876543"
                output = result.stdout.strip()
                if "result:" in output:
                    parts = output.split("result:")[-1].strip().split()
                    if len(parts) >= 2:
                        predicted_text = parts[0]
                        confidence = float(parts[1]) if parts[1] != 'nan' else 0.0
                        return predicted_text, confidence
                        
            logger.warning(f"⚠️ Inference failed for {image_path}: {result.stderr}")
            return "", 0.0
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout for {image_path}")
            return "", 0.0
        except Exception as e:
            logger.error(f"❌ Error testing {image_path}: {e}")
            return "", 0.0
            
    def run_batch_test(self, validation_data: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Run batch testing with validation data"""
        logger.info(f"🧪 Starting batch testing with {len(validation_data)} samples...")
        
        results = []
        correct_predictions = 0
        total_processed = 0
        
        for i, (img_path, ground_truth) in enumerate(validation_data, 1):
            logger.info(f"[{i:2d}/{len(validation_data)}] Testing: {img_path}")
            logger.info(f"   Ground Truth: '{ground_truth}'")
            
            predicted_text, confidence = self.test_single_image(img_path)
            
            if predicted_text:
                total_processed += 1
                is_correct = predicted_text == ground_truth
                if is_correct:
                    correct_predictions += 1
                    
                char_accuracy = 100.0 if is_correct else 0.0
                
                result = {
                    'image': img_path,
                    'ground_truth': ground_truth,
                    'predicted': predicted_text,
                    'confidence': confidence,
                    'correct': is_correct,
                    'character_accuracy': char_accuracy
                }
                results.append(result)
                
                status = "✅" if is_correct else "❌"
                logger.info(f"   {status} Predicted: '{predicted_text}'")
                logger.info(f"   📊 Confidence: {confidence:.4f} | Char Acc: {char_accuracy:.1f}%")
                
            else:
                logger.warning(f"   ⚠️ Failed to get prediction")
                
        # Calculate final metrics
        accuracy = correct_predictions / total_processed if total_processed > 0 else 0.0
        success_rate = total_processed / len(validation_data)
        
        summary = {
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'total_samples': len(validation_data),
            'processed_samples': total_processed,
            'correct_predictions': correct_predictions,
            'accuracy': accuracy,
            'success_rate': success_rate,
            'exact_match_rate': accuracy,  # Same as accuracy for single characters
            'results': results
        }
        
        return summary
        
    def save_results(self, summary: Dict[str, Any]):
        """Save test results to file"""
        timestamp = summary['timestamp']
        results_file = self.project_root / f"numbers_model_test_results_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        logger.info(f"💾 Results saved to: {results_file}")
        
        # Print summary
        print(f"\n{'=' * 80}")
        print(f"🎯 NUMBERS MODEL TEST RESULTS")
        print(f"{'=' * 80}")
        print(f"📊 OVERALL PERFORMANCE:")
        print(f"  • Total samples tested: {summary['total_samples']}")
        print(f"  • Successful inferences: {summary['processed_samples']}")
        print(f"  • Success rate: {summary['success_rate']:.1%}")
        print(f"  • Character accuracy: {summary['accuracy']:.1%}")
        print(f"  • Exact matches: {summary['correct_predictions']}/{summary['total_samples']}")
        
        print(f"\n🎯 PERFORMANCE ASSESSMENT:")
        if summary['success_rate'] > 0.9:
            print(f"  ✅ Model loading: EXCELLENT")
        elif summary['success_rate'] > 0.7:
            print(f"  ⚠️ Model loading: GOOD")
        else:
            print(f"  ❌ Model loading: NEEDS IMPROVEMENT")
            
        if summary['accuracy'] > 0.8:
            print(f"  ✅ Character accuracy: EXCELLENT")
        elif summary['accuracy'] > 0.5:
            print(f"  ⚠️ Character accuracy: GOOD")
        else:
            print(f"  ❌ Character accuracy: NEEDS IMPROVEMENT")
            
        # Show some sample results
        print(f"\n📁 SAMPLE PREDICTIONS:")
        for result in summary['results'][:10]:
            status = "✅" if result['correct'] else "❌"
            print(f"  {status} {result['image']}")
            print(f"     GT: '{result['ground_truth']}'")
            print(f"     Predicted: '{result['predicted']}'")
            print(f"     Conf: {result['confidence']:.4f} | Acc: {result['character_accuracy']:.1f}%")
            
    def run_test(self):
        """Run complete numbers model test"""
        print(f"🚀 Numbers Model Tester for Thai OCR")
        print(f"{'=' * 60}")
        
        # Check prerequisites
        logger.info("🔍 Checking prerequisites...")
        
        if not self.paddleocr_dir.exists():
            logger.error(f"❌ PaddleOCR directory not found: {self.paddleocr_dir}")
            return
            
        # Check if model files exist
        best_accuracy_file = self.model_dir / "best_accuracy.pdparams"
        if not best_accuracy_file.exists():
            logger.error(f"❌ Model file not found: {best_accuracy_file}")
            return
            
        if not self.validation_file.exists():
            logger.error(f"❌ Validation file not found: {self.validation_file}")
            return
            
        logger.info(f"✅ PaddleOCR directory: {self.paddleocr_dir}")
        logger.info(f"✅ Model file: {best_accuracy_file}")
        logger.info(f"✅ Validation file: {self.validation_file}")
        
        # Create numbers dictionary and config
        self.create_numbers_dictionary()
        self.create_inference_config()
        
        # Load validation data
        validation_data = self.load_validation_data(max_samples=15)
        if not validation_data:
            logger.error("❌ No validation data loaded")
            return
            
        # Run tests
        summary = self.run_batch_test(validation_data)
        
        # Save and display results
        self.save_results(summary)
        
        print(f"\n✅ Testing completed!")
        print(f"📁 Check detailed results in the generated JSON file")


def main():
    """Main function"""
    tester = NumbersModelTester()
    tester.run_test()


if __name__ == "__main__":
    main()
