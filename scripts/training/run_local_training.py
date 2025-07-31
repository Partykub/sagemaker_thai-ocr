#!/usr/bin/env python3
"""
🚀 Run Local Training - Task 4.1
เรียกใช้การเทรน PaddleOCR แบบ local สำหรับ Thai OCR

Based on development-task.md Section 4.1:
- Local training: python PaddleOCR/tools/train.py -c configs/rec/thai_rec.yml
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional
import time
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalTrainingRunner:
    """จัดการการเทรน PaddleOCR แบบ local"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.configs_dir = self.project_root / "configs" / "rec"
        self.paddleocr_dir = self.project_root / "PaddleOCR"
        self.train_script = self.paddleocr_dir / "tools" / "train.py"
        
    def check_prerequisites(self) -> bool:
        """ตรวจสอบข้อกำหนดเบื้องต้น"""
        logger.info("🔍 Checking prerequisites for local training...")
        
        issues = []
        
        # 1. Check PaddleOCR installation
        try:
            import paddle
            import paddleocr
            logger.info(f"  ✅ PaddlePaddle version: {paddle.__version__}")
            logger.info(f"  ✅ PaddleOCR installed")
        except ImportError as e:
            issues.append(f"Missing package: {e}")
        
        # 2. Check PaddleOCR repository
        if not self.paddleocr_dir.exists():
            issues.append("PaddleOCR repository not found. Run: git clone https://github.com/PaddlePaddle/PaddleOCR.git")
        elif not self.train_script.exists():
            issues.append(f"Training script not found: {self.train_script}")
        else:
            logger.info(f"  ✅ PaddleOCR repository: {self.paddleocr_dir}")
        
        # 3. Check config files
        if not self.configs_dir.exists():
            issues.append("Configs directory not found. Run Task 3 first: python scripts/training/setup_training_config.py")
        else:
            configs = list(self.configs_dir.glob("thai_rec*.yml"))
            if configs:
                logger.info(f"  ✅ Found {len(configs)} config files")
                for config in configs:
                    logger.info(f"    - {config.name}")
            else:
                issues.append("No Thai recognition configs found")
        
        # 4. Check GPU availability
        gpu_available = self._check_gpu()
        if gpu_available:
            logger.info("  ✅ GPU available for training")
        else:
            logger.info("  ⚠️ No GPU detected - will use CPU (slower)")
        
        # 5. Check dataset
        dataset_valid = self._check_dataset()
        if dataset_valid:
            logger.info("  ✅ Dataset validation passed")
        else:
            issues.append("Dataset validation failed")
        
        if issues:
            logger.error("❌ Prerequisites check failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        else:
            logger.info("✅ All prerequisites satisfied!")
            return True
    
    def _check_gpu_system(self) -> bool:
        """ตรวจสอบ GPU availability ในระบบ (ไม่ต้องใช้ paddle)"""
        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _check_gpu(self) -> bool:
        """ตรวจสอบ GPU availability"""
        try:
            import paddle
            gpu_count = paddle.device.cuda.device_count()
            return gpu_count > 0
        except:
            try:
                result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
                return result.returncode == 0
            except FileNotFoundError:
                return False
    
    def _check_dataset(self) -> bool:
        """ตรวจสอบ dataset"""
        # หา dataset directory
        converted_dir = self.project_root / "thai-letters" / "datasets" / "converted"
        dataset_dirs = list(converted_dir.glob("train_data_thai_paddleocr_*"))
        
        if not dataset_dirs:
            logger.error("No converted datasets found")
            return False
        
        latest_dataset = max(dataset_dirs, key=os.path.getctime)
        
        # ตรวจสอบไฟล์จำเป็น
        required_files = [
            "train_data/th_dict.txt",
            "train_data/rec/rec_gt_train.txt",
            "train_data/rec/rec_gt_val.txt",
            "train_data/rec/thai_data/train",
            "train_data/rec/thai_data/val"
        ]
        
        for file_path in required_files:
            full_path = latest_dataset / file_path
            if not full_path.exists():
                logger.error(f"Missing: {full_path}")
                return False
        
        logger.info(f"  📂 Dataset: {latest_dataset.name}")
        return True
    
    def setup_paddleocr(self, force_cpu: bool = False) -> bool:
        """ติดตั้งและเตรียม PaddleOCR"""
        logger.info("📦 Setting up PaddleOCR...")
        
        if force_cpu:
            paddle_package = "paddlepaddle"
            logger.info("💻 Force CPU installation requested")
        else:
            # ตรวจสอบ GPU ก่อนเลือก package
            gpu_available = self._check_gpu_system()
            
            if gpu_available:
                paddle_package = "paddlepaddle-gpu"
                logger.info("🎮 GPU detected - installing GPU version")
                logger.info("⚠️ Note: If GPU version fails due to CUDA compatibility, use --force-cpu")
            else:
                paddle_package = "paddlepaddle"
                logger.info("💻 No GPU detected - installing CPU version")
        
        # ติดตั้ง packages
        packages = [paddle_package, "paddleocr"]
        
        # ติดตั้ง PaddleOCR dependencies ที่จำเป็น
        additional_deps = [
            "scikit-image",
            "opencv-python", 
            "Pillow",
            "numpy",
            "matplotlib",
            "pyyaml",
            "lmdb", 
            "imgaug",
            "albumentations",
            "rapidfuzz"
        ]
        
        all_packages = packages + additional_deps
        
        for package in all_packages:
            logger.info(f"Installing {package}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to install {package}")
                logger.error(f"Error: {result.stderr}")
                
                # ถ้าติดตั้ง GPU version ไม่ได้ ลองติดตั้ง CPU version แทน
                if package == "paddlepaddle-gpu":
                    logger.info("🔄 GPU installation failed, trying CPU version...")
                    result = subprocess.run([sys.executable, "-m", "pip", "install", "paddlepaddle"], 
                                          capture_output=True, text=True)
                    if result.returncode != 0:
                        logger.error(f"CPU installation also failed: {result.stderr}")
                        return False
                    else:
                        logger.info("✅ CPU version installed successfully")
                else:
                    # สำหรับ dependencies อื่นๆ ถ้าติดตั้งไม่ได้ ให้ warning แต่ไม่หยุด
                    if package in additional_deps:
                        logger.warning(f"⚠️ Failed to install {package}, continuing...")
                        continue
                    else:
                        return False
            else:
                logger.info(f"✅ {package} installed successfully")
        
        # Clone PaddleOCR repository
        if not self.paddleocr_dir.exists():
            logger.info("Cloning PaddleOCR repository...")
            result = subprocess.run([
                "git", "clone", 
                "https://github.com/PaddlePaddle/PaddleOCR.git",
                str(self.paddleocr_dir)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to clone PaddleOCR: {result.stderr}")
                return False
        
        logger.info("✅ PaddleOCR setup completed!")
        return True
    
    def run_training(self, config_type: str = "dev", use_gpu: Optional[bool] = None) -> bool:
        """เรียกใช้การเทรน"""
        logger.info(f"🚀 Starting local training with {config_type} config...")
        
        # เลือก config file
        config_files = {
            "dev": "thai_rec_dev.yml",
            "main": "thai_rec.yml", 
            "prod": "thai_rec_prod.yml"
        }
        
        if config_type not in config_files:
            logger.error(f"Invalid config type: {config_type}. Choose from: {list(config_files.keys())}")
            return False
        
        config_path = self.configs_dir / config_files[config_type]
        if not config_path.exists():
            logger.error(f"Config file not found: {config_path}")
            return False
        
        # สร้างคำสั่งเทรน
        logger.info(f"📋 Config file: {config_path}")
        
        # แสดงคำสั่ง
        logger.info(f"🎯 Will run training from PaddleOCR directory with relative config path")
        
        # สร้าง output directory
        output_dir = self.project_root / "output" / f"{config_type}_training"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # เรียกใช้การเทรน
        logger.info("🎯 Starting training process...")
        logger.info("📊 Monitor training progress in the logs below:")
        logger.info("="*60)
        
        try:
            # เปลี่ยน working directory เป็น PaddleOCR
            original_cwd = os.getcwd()
            os.chdir(str(self.paddleocr_dir))
            
            # สร้างคำสั่งให้ใช้ relative path จาก PaddleOCR directory
            relative_config_path = os.path.relpath(str(config_path), str(self.paddleocr_dir))
            
            cmd = [
                sys.executable,
                "tools/train.py",
                "-c", relative_config_path
            ]
            
            # ตั้งค่า GPU
            if use_gpu is False:
                cmd.extend(["-o", "Global.use_gpu=false"])
            elif use_gpu is True:
                cmd.extend(["-o", "Global.use_gpu=true"])
            
            logger.info(f"📋 Training command (from PaddleOCR directory):")
            logger.info(f"  {' '.join(cmd)}")
            
            start_time = time.time()
            
            # รันการเทรน
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # แสดงผล log แบบ real-time
            for line in process.stdout:
                print(line, end='')
                sys.stdout.flush()
            
            process.wait()
            
            # กลับไป original directory
            os.chdir(original_cwd)
            
            duration = time.time() - start_time
            
            if process.returncode == 0:
                logger.info("="*60)
                logger.info(f"🎉 Training completed successfully!")
                logger.info(f"⏱️ Duration: {duration/60:.1f} minutes")
                logger.info(f"📁 Model saved in PaddleOCR/output/")
                return True
            else:
                logger.error("="*60)
                logger.error(f"❌ Training failed with return code: {process.returncode}")
                return False
                
        except Exception as e:
            os.chdir(original_cwd)
            logger.error(f"❌ Training error: {e}")
            return False
    
    def generate_training_report(self, config_type: str, success: bool) -> None:
        """สร้างรายงานการเทรน"""
        status = "COMPLETED" if success else "FAILED"
        report_content = f"""# Task 4.1: Local Training - Report

**Status**: {status} ✅ 
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🚀 Training Configuration
- **Config Type**: {config_type}
- **Config File**: `configs/rec/thai_rec_{config_type}.yml`
- **Framework**: PaddleOCR
- **Model**: SVTR_LCNet (Thai Recognition)

## 📊 Training Details
- **Dataset**: 7,014 train + 1,754 val images
- **Characters**: 880 Thai characters
- **Train/Val Split**: 80/20

## 📁 Output Locations
- **Model**: `PaddleOCR/output/thai_rec_{config_type}_output/`
- **Logs**: Console output above
- **Config**: `configs/rec/thai_rec_{config_type}.yml`

## 🎯 Next Steps
{self._get_next_steps(success)}

---
*Generated by scripts/training/run_local_training.py - Task 4.1*
"""
        
        report_path = self.project_root / f"TASK4_LOCAL_TRAINING_{config_type.upper()}_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"📋 Training report saved: {report_path}")
    
    def _get_next_steps(self, success: bool) -> str:
        if success:
            return """1. **Test model inference** with trained weights
2. **Evaluate model performance** on validation set  
3. **Proceed to SageMaker training** if needed
4. **Update development-task.md** - mark Local training as completed"""
        else:
            return """1. **Check training logs** for error details
2. **Verify dataset and config** files
3. **Try with different config** (dev/main/prod)
4. **Check GPU/CPU availability** and memory"""

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🚀 Run Local Training for Thai OCR")
    parser.add_argument("--config", type=str, default="dev", 
                       choices=["dev", "main", "prod"],
                       help="Config type to use (default: dev)")
    parser.add_argument("--setup", action="store_true",
                       help="Setup PaddleOCR before training")
    parser.add_argument("--force-cpu", action="store_true",
                       help="Force CPU version installation (for CUDA compatibility issues)")
    parser.add_argument("--gpu", type=str, default=None,
                       choices=["true", "false"],
                       help="Force GPU usage (true/false)")
    parser.add_argument("--check-only", action="store_true",
                       help="Only check prerequisites, don't train")
    
    args = parser.parse_args()
    
    logger.info("🚀 Task 4.1: Local Training Setup")
    logger.info("="*50)
    
    runner = LocalTrainingRunner()
    
    # Setup PaddleOCR if requested
    if args.setup:
        if not runner.setup_paddleocr(force_cpu=args.force_cpu):
            logger.error("❌ PaddleOCR setup failed")
            return
    
    # Check prerequisites
    if not runner.check_prerequisites():
        logger.error("❌ Prerequisites check failed")
        if not args.setup:
            logger.info("💡 Try running with --setup to install requirements")
        return
    
    if args.check_only:
        logger.info("✅ Prerequisites check completed!")
        return
    
    # Convert GPU argument
    use_gpu = None
    if args.gpu == "true":
        use_gpu = True
    elif args.gpu == "false":
        use_gpu = False
    
    # Run training
    success = runner.run_training(args.config, use_gpu)
    
    # Generate report
    runner.generate_training_report(args.config, success)
    
    if success:
        logger.info("🎉 Task 4.1: Local Training - COMPLETED!")
    else:
        logger.error("❌ Task 4.1: Local Training - FAILED!")

if __name__ == "__main__":
    main()
