#!/usr/bin/env python3
"""
🧪 Test SageMaker Trained Thai OCR Model
ทดสอบโมเดล Thai OCR ที่เทรนจาก SageMaker

Uses:
- Model: models/sagemaker_trained/best_model/
- Config: CRNN + MobileNetV3 (same as training)
- Dictionary: thai-letters/th_dict.txt (880 chars)
- Validation data: with ground truth labels
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SageMakerModelTester:
    """ทดสอบโมเดลที่เทรนจาก SageMaker"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.paddleocr_dir = self.project_root / "PaddleOCR"
        self.model_dir = self.project_root / "models" / "sagemaker_trained" / "best_model"
        self.config_file = self.project_root / "corrected_inference_config.yml"
        self.dict_file = self.project_root / "thai-letters" / "th_dict.txt"
        self.val_label_file = self.project_root / "thai-letters" / "datasets" / "converted" / "train_data_thai_paddleocr_0804_1144" / "train_data" / "rec" / "rec_gt_val.txt"
        self.results = []
        
    def check_prerequisites(self) -> bool:
        """ตรวจสอบไฟล์ที่จำเป็น"""
        logger.info("🔍 Checking prerequisites...")
        
        checks = [
            (self.paddleocr_dir, "PaddleOCR directory"),
            (self.model_dir / "model.pdparams", "Model parameters"),
            (self.dict_file, "Thai dictionary"),
            (self.val_label_file, "Validation labels"),
        ]
        
        all_good = True
        for path, description in checks:
            if path.exists():
                size = path.stat().st_size if path.is_file() else "Directory"
                logger.info(f"✅ {description}: {path} ({size} bytes)" if size != "Directory" else f"✅ {description}: {path}")
            else:
                logger.error(f"❌ {description}: {path} NOT FOUND")
                all_good = False
        
        # Check if inference config exists, if not create one
        if not self.config_file.exists():
            logger.warning(f"⚠️ Config file not found: {self.config_file}")
            logger.info("📝 Will create inference config automatically")
        
        return all_good
    
    def load_validation_data(self, max_samples: int = 20) -> List[Tuple[str, str]]:
        """โหลดข้อมูล validation พร้อม ground truth"""
        logger.info(f"📁 Loading validation data (max {max_samples} samples)...")
        
        validation_data = []
        
        try:
            with open(self.val_label_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:max_samples]
                
            for line in lines:
                line = line.strip()
                if '\t' in line:
                    # Format: image_path\tground_truth_text
                    parts = line.split('\t', 1)
                    if len(parts) == 2:
                        rel_image_path, ground_truth = parts
                        
                        # Convert relative path to absolute
                        # rel_image_path format: thai_data/val/346_01.jpg
                        full_image_path = self.project_root / "thai-letters" / "datasets" / "converted" / "train_data_thai_paddleocr_0804_1144" / "train_data" / "rec" / rel_image_path
                        
                        if full_image_path.exists():
                            validation_data.append((str(full_image_path), ground_truth))
                        else:
                            logger.warning(f"Image not found: {full_image_path}")
                            
            logger.info(f"✅ Loaded {len(validation_data)} validation samples")
            
            # Show first few samples
            for i, (img_path, gt) in enumerate(validation_data[:3]):
                logger.info(f"  Sample {i+1}: {Path(img_path).name} -> '{gt}'")
            
            return validation_data
            
        except Exception as e:
            logger.error(f"Failed to load validation data: {e}")
            return []
    
    def create_inference_config(self) -> str:
        """สร้างคอนฟิกสำหรับ inference"""
        logger.info("⚙️ Creating inference configuration...")
        
        # Use corrected config instead of creating new one
        if self.config_file.exists():
            logger.info(f"✅ Using corrected config: {self.config_file}")
            return str(self.config_file)
        
        # Fallback: create config only if corrected one doesn't exist
        config_content = f"""Global:
  use_gpu: false
  epoch_num: 100
  log_smooth_window: 20
  print_batch_step: 10
  save_model_dir: ./output/thai_rec/
  save_epoch_step: 10
  eval_batch_step: 500
  cal_metric_during_train: true
  pretrained_model: {self.model_dir}/model
  character_dict_path: {self.dict_file}
  character_type: thai
  max_text_length: 25
  infer_mode: true
  use_space_char: false
  distributed: false
  save_res_path: ./inference_results.txt
  infer_img: ./test_images/

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: 0.001
    warmup_epoch: 5
  regularizer:
    name: L2
    factor: 3.0e-05

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
    - CTCLabelEncode:
    - RecResizeImg:
        image_shape: [3, 32, 100]
    - KeepKeys:
        keep_keys:
        - image
        - label
        - length
  loader:
    shuffle: true
    batch_size_per_card: 256
    drop_last: true
    num_workers: 8

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
        image_shape: [3, 32, 100]
    - KeepKeys:
        keep_keys:
        - image
        - label
        - length
  loader:
    shuffle: false
    drop_last: false
    batch_size_per_card: 256
    num_workers: 4
"""
        
        # Save config
        test_config_file = self.project_root / "test_inference_config.yml"
        with open(test_config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
            
        logger.info(f"✅ Config created: {test_config_file}")
        return str(test_config_file)
    
    def run_inference_on_image(self, image_path: str, config_file: str) -> Dict:
        """รัน inference บนภาพเดียว"""
        
        try:
            # Build command - use relative paths from PaddleOCR directory
            rel_config = os.path.relpath(config_file, self.paddleocr_dir)
            rel_image = os.path.relpath(image_path, self.paddleocr_dir)
            
            cmd = [
                "python", "tools/infer_rec.py",
                "-c", rel_config,
                "-o", f"Global.infer_img={rel_image}"
            ]
            
            logger.debug(f"Running: {' '.join(cmd)} (cwd: {self.paddleocr_dir})")
            
            # Run inference
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.paddleocr_dir),
                timeout=30
            )
            
            # Parse result
            if result.returncode == 0 and "result:" in result.stdout:
                # Extract prediction from output
                for line in result.stdout.split('\n'):
                    if "result:" in line:
                        # Format: "result: predicted_text confidence_score"
                        result_part = line.split("result:")[1].strip()
                        
                        # Try to split text and confidence
                        parts = result_part.rsplit(' ', 1)
                        if len(parts) == 2:
                            predicted_text, confidence_str = parts
                            try:
                                confidence = float(confidence_str)
                            except ValueError:
                                predicted_text = result_part
                                confidence = 0.0
                        else:
                            predicted_text = result_part
                            confidence = 0.0
                        
                        # สำหรับ single character เอาแค่ตัวแรก
                        if predicted_text:
                            single_char = predicted_text[0] if predicted_text else ""
                            
                            return {
                                "success": True,
                                "predicted_text": single_char,  # เปลี่ยนเป็น single char
                                "full_prediction": predicted_text,  # เก็บ full prediction ไว้ด้วย
                                "confidence": confidence,
                                "raw_output": result.stdout
                            }
            
            return {
                "success": False,
                "error": result.stderr if result.stderr else "No result found in output",
                "raw_output": result.stdout,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Inference timeout (30s)",
                "raw_output": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "raw_output": ""
            }
    
    def calculate_accuracy(self, predicted: str, ground_truth: str) -> Dict:
        """คำนวณความแม่นยำ"""
        
        # Character-level accuracy
        char_correct = 0
        max_len = max(len(predicted), len(ground_truth))
        
        if max_len == 0:
            char_accuracy = 1.0 if predicted == ground_truth else 0.0
        else:
            for i in range(min(len(predicted), len(ground_truth))):
                if i < len(predicted) and i < len(ground_truth):
                    if predicted[i] == ground_truth[i]:
                        char_correct += 1
            char_accuracy = char_correct / max_len
        
        # Exact match
        exact_match = predicted == ground_truth
        
        # Edit distance (simple)
        edit_distance = abs(len(predicted) - len(ground_truth))
        for i in range(min(len(predicted), len(ground_truth))):
            if predicted[i] != ground_truth[i]:
                edit_distance += 1
        
        return {
            "character_accuracy": char_accuracy,
            "exact_match": exact_match,
            "edit_distance": edit_distance,
            "predicted_length": len(predicted),
            "ground_truth_length": len(ground_truth)
        }
    
    def run_batch_test(self, max_samples: int = 10) -> Dict:
        """รันการทดสอบแบบ batch"""
        logger.info(f"🧪 Starting batch testing (max {max_samples} samples)...")
        
        # Load validation data
        validation_data = self.load_validation_data(max_samples)
        if not validation_data:
            return {"error": "No validation data loaded"}
        
        # Create inference config
        config_file = self.create_inference_config()
        
        # Test each sample
        results = []
        successful_inferences = 0
        total_character_accuracy = 0.0
        exact_matches = 0
        
        print(f"\n{'='*80}")
        print(f"🧪 TESTING {len(validation_data)} SAMPLES")
        print(f"{'='*80}")
        
        for i, (image_path, ground_truth) in enumerate(validation_data):
            print(f"\n[{i+1:2d}/{len(validation_data)}] Testing: {Path(image_path).name}")
            print(f"   Ground Truth: '{ground_truth}'")
            
            # Run inference
            inference_result = self.run_inference_on_image(image_path, config_file)
            
            # Calculate accuracy if successful
            if inference_result["success"]:
                successful_inferences += 1
                predicted_text = inference_result["predicted_text"]
                
                accuracy_metrics = self.calculate_accuracy(predicted_text, ground_truth)
                
                total_character_accuracy += accuracy_metrics["character_accuracy"]
                if accuracy_metrics["exact_match"]:
                    exact_matches += 1
                
                # Store result
                result = {
                    "image": Path(image_path).name,
                    "ground_truth": ground_truth,
                    "predicted": predicted_text,
                    "confidence": inference_result["confidence"],
                    "metrics": accuracy_metrics,
                    "success": True
                }
                
                # Status icon
                status_icon = "✅" if accuracy_metrics["exact_match"] else "⚠️"
                print(f"   {status_icon} Predicted: '{predicted_text}'")
                print(f"   📊 Confidence: {inference_result['confidence']:.4f} | Char Acc: {accuracy_metrics['character_accuracy']:.1%}")
                
            else:
                result = {
                    "image": Path(image_path).name,
                    "ground_truth": ground_truth,
                    "predicted": "",
                    "confidence": 0.0,
                    "error": inference_result["error"],
                    "success": False
                }
                
                print(f"   ❌ ERROR: {inference_result['error'][:60]}...")
                if inference_result.get('raw_output'):
                    print(f"      Raw output: {inference_result['raw_output'][:100]}...")
            
            results.append(result)
        
        # Calculate overall metrics
        avg_character_accuracy = total_character_accuracy / max(successful_inferences, 1)
        exact_match_rate = exact_matches / len(validation_data)
        success_rate = successful_inferences / len(validation_data)
        
        summary = {
            "total_samples": len(validation_data),
            "successful_inferences": successful_inferences,
            "success_rate": success_rate,
            "average_character_accuracy": avg_character_accuracy,
            "exact_match_rate": exact_match_rate,
            "exact_matches": exact_matches
        }
        
        return {
            "summary": summary,
            "detailed_results": results,
            "config_used": config_file
        }
    
    def print_summary_report(self, test_results: Dict):
        """แสดงรายงานสรุป"""
        print("\n" + "="*80)
        print("🎯 SAGEMAKER THAI OCR MODEL TEST RESULTS")
        print("="*80)
        
        if "error" in test_results:
            print(f"❌ Test failed: {test_results['error']}")
            return
        
        summary = test_results["summary"]
        
        print(f"📊 OVERALL PERFORMANCE:")
        print(f"  • Total samples tested: {summary['total_samples']}")
        print(f"  • Successful inferences: {summary['successful_inferences']}")
        print(f"  • Success rate: {summary['success_rate']:.1%}")
        print(f"  • Average character accuracy: {summary['average_character_accuracy']:.1%}")
        print(f"  • Exact match rate: {summary['exact_match_rate']:.1%}")
        print(f"  • Exact matches: {summary['exact_matches']}/{summary['total_samples']}")
        
        # Performance assessment
        print(f"\n🎯 PERFORMANCE ASSESSMENT:")
        if summary['success_rate'] >= 0.8:
            print("  ✅ Model loading: GOOD")
        else:
            print("  ❌ Model loading: ISSUES DETECTED")
            
        if summary['average_character_accuracy'] >= 0.7:
            print("  ✅ Character accuracy: EXCELLENT")
        elif summary['average_character_accuracy'] >= 0.5:
            print("  ⚠️ Character accuracy: MODERATE")
        else:
            print("  ❌ Character accuracy: NEEDS IMPROVEMENT")
            
        if summary['exact_match_rate'] >= 0.5:
            print("  ✅ Exact matches: EXCELLENT")
        elif summary['exact_match_rate'] >= 0.3:
            print("  ⚠️ Exact matches: MODERATE")
        else:
            print("  ❌ Exact matches: NEEDS IMPROVEMENT")
        
        print(f"\n📁 SAMPLE PREDICTIONS:")
        successful_results = [r for r in test_results["detailed_results"] if r["success"]]
        
        for i, result in enumerate(successful_results[:8]):  # Show first 8
            status = "✅" if result["metrics"]["exact_match"] else "⚠️"
            print(f"  {status} {result['image']}")
            print(f"     GT: '{result['ground_truth']}'")
            print(f"     Predicted: '{result['predicted']}'")
            print(f"     Conf: {result['confidence']:.4f} | Acc: {result['metrics']['character_accuracy']:.1%}")
        
        if len(successful_results) > 8:
            print(f"  ... and {len(successful_results) - 8} more successful predictions")
        
        failed_results = [r for r in test_results["detailed_results"] if not r["success"]]
        if failed_results:
            print(f"\n❌ FAILED PREDICTIONS:")
            for result in failed_results[:3]:
                print(f"  • {result['image']}: {result['error'][:50]}...")
        
        print(f"\n⚙️ MODEL CONFIGURATION:")
        print(f"  • Model: models/sagemaker_trained/best_model/")
        print(f"  • Architecture: CRNN + MobileNetV3")
        print(f"  • Dictionary: thai-letters/th_dict.txt")
        print(f"  • Max text length: 1")
        print(f"  • Config: {Path(test_results['config_used']).name}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if summary['average_character_accuracy'] < 0.5:
            print("  ⚠️ Consider improving accuracy:")
            print("     - Retrain with optimized 74-char dictionary")
            print("     - Adjust preprocessing parameters")
            print("     - Use data augmentation")
        
        if summary['success_rate'] < 0.8:
            print("  ⚠️ Fix inference issues:")
            print("     - Check PaddleOCR version compatibility")
            print("     - Verify model file integrity")
            print("     - Update configuration settings")
        
        if summary['exact_match_rate'] > 0.3:
            print("  ✅ Model shows promising results!")
            print("     - Consider deploying to SageMaker endpoint")
            print("     - Test with real-world images")
    
    def save_results(self, test_results: Dict, filename: str = None):
        """บันทึกผลลัพธ์"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"sagemaker_model_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Results saved to: {filename}")
        return filename

def main():
    """Main function"""
    print("🚀 SageMaker Thai OCR Model Tester")
    print("=" * 60)
    
    tester = SageMakerModelTester()
    
    # Check prerequisites
    if not tester.check_prerequisites():
        print("❌ Prerequisites check failed. Please ensure all required files exist.")
        return
    
    print("\n🧪 Starting model testing...")
    
    # Run batch test
    test_results = tester.run_batch_test(max_samples=15)
    
    # Print summary
    tester.print_summary_report(test_results)
    
    # Save results
    if "error" not in test_results:
        result_file = tester.save_results(test_results)
        print(f"\n📄 Detailed results saved to: {result_file}")
    
    print(f"\n✅ Testing completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
