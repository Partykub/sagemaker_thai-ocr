#!/usr/bin/env python3
"""
🚀 Easy Thai OCR Single Character Training Workflow
สคริปต์เดียวจบ: จากข้อมูล → เทรน → ทดสอบ (SINGLE CHARACTER ONLY)
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import boto3
import yaml

class EasySingleCharTraining:
    def __init__(self):
        self.setup_logging()
        self.project_root = Path(__file__).parent.parent
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def step_1_prepare_single_char_data(self):
        """📊 Step 1: เตรียมข้อมูล single character"""
        self.logger.info("🎯 Step 1: เตรียมข้อมูล Single Character")
        
        # สร้าง single character dataset
        output_dir = self.project_root / f"thai-letters/datasets/single_char_{self.timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # รัน generator สำหรับ single character
        self.logger.info("📝 สร้างข้อมูล single character...")
        
        cmd = [
            "python", "thai-letters/quick_phase1_generator.py", 
            "10"  # สร้าง 10 samples ต่อตัวอักษร
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.project_root))
        if result.returncode != 0:
            raise Exception(f"❌ สร้างข้อมูลล้มเหลว: {result.stderr}")
            
        # หา dataset ที่สร้างใหม่
        datasets_dir = self.project_root / "thai-letters/datasets/converted"
        latest_dataset = None
        
        for dataset_dir in sorted(datasets_dir.glob("train_data_thai_paddleocr_*"), reverse=True):
            if dataset_dir.is_dir():
                latest_dataset = dataset_dir
                break
        
        if not latest_dataset:
            raise FileNotFoundError("❌ ไม่พบ dataset ที่สร้างใหม่")
            
        self.logger.info(f"✅ พบ dataset: {latest_dataset.name}")
        
        # แปลงเป็น single character format
        train_data_dir = latest_dataset / "train_data/rec"
        single_char_dir = self.project_root / f"thai-letters/datasets/single_char_{self.timestamp}/train_data/rec"
        single_char_dir.mkdir(parents=True, exist_ok=True)
        
        # คัดลอกข้อมูลและแก้ไข label files เป็น single character
        import shutil
        
        # คัดลอก images
        if (train_data_dir / "thai_data").exists():
            shutil.copytree(train_data_dir / "thai_data", single_char_dir / "thai_data")
        
        # แก้ไข label files เป็น single character
        self._convert_to_single_char_labels(train_data_dir, single_char_dir)
        
        # คัดลอก dictionary
        shutil.copy(self.project_root / "thai-letters/th_dict.txt", single_char_dir / "th_dict.txt")
        
        # อัปโหลดไป S3
        s3_bucket = "paddleocr-dev-data-bucket"
        s3_prefix = f"data/single_char_{self.timestamp}"
        
        self.logger.info(f"📤 อัปโหลดข้อมูลไป s3://{s3_bucket}/{s3_prefix}/")
        
        cmd = [
            "aws", "s3", "sync", 
            str(single_char_dir),
            f"s3://{s3_bucket}/{s3_prefix}/",
            "--quiet"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"❌ อัปโหลด S3 ล้มเหลว: {result.stderr}")
            
        self.logger.info("✅ อัปโหลดข้อมูลเสร็จสิ้น")
        return s3_bucket, s3_prefix
    
    def _convert_to_single_char_labels(self, source_dir, target_dir):
        """แปลง label files เป็น single character"""
        self.logger.info("🔧 แปลง labels เป็น single character...")
        
        label_files = ["rec_gt_train.txt", "rec_gt_val.txt"]
        
        for label_file in label_files:
            source_file = source_dir / label_file
            target_file = target_dir / label_file
            
            if source_file.exists():
                with open(source_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                single_char_lines = []
                for line in lines:
                    line = line.strip()
                    if '\t' in line:
                        img_path, text = line.split('\t', 1)
                        # เอาแค่ตัวอักษรแรก
                        if text:
                            first_char = text[0]
                            single_char_lines.append(f"{img_path}\t{first_char}\n")
                
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.writelines(single_char_lines)
                    
                self.logger.info(f"✅ แปลง {label_file}: {len(single_char_lines)} samples")

    def step_2_create_single_char_config(self):
        """⚙️ Step 2: สร้าง single character training config"""
        self.logger.info("🎯 Step 2: สร้าง Single Character Training Configuration")
        
        config = {
            "Global": {
                "use_gpu": False,
                "epoch_num": 100,  # เพิ่ม epochs สำหรับ single char
                "log_smooth_window": 20,
                "print_batch_step": 10,
                "save_model_dir": "/opt/ml/model/",
                "save_epoch_step": 20,
                "eval_batch_step": [0, 1000],
                "cal_metric_during_train": True,
                "character_dict_path": "/opt/ml/input/data/training/th_dict.txt",
                "character_type": "thai",
                "max_text_length": 1,  # SINGLE CHARACTER ONLY
                "use_space_char": False,
                "distributed": False
            },
            "Architecture": {
                "model_type": "rec",
                "algorithm": "CRNN",
                "Backbone": {
                    "name": "MobileNetV3",
                    "scale": 0.5,
                    "model_name": "large"
                },
                "Neck": {
                    "name": "SequenceEncoder",
                    "encoder_type": "rnn", 
                    "hidden_size": 48  # ลดขนาดสำหรับ single char
                },
                "Head": {
                    "name": "CTCHead",
                    "fc_decay": 0.00001
                }
            },
            "Loss": {"name": "CTCLoss"},
            "PostProcess": {"name": "CTCLabelDecode"},
            "Metric": {
                "name": "RecMetric",
                "main_indicator": "acc"
            },
            "Optimizer": {
                "name": "Adam",
                "beta1": 0.9,
                "beta2": 0.999,
                "lr": {
                    "name": "Cosine",
                    "learning_rate": 0.0005,  # ลด learning rate
                    "warmup_epoch": 10
                },
                "regularizer": {
                    "name": "L2",
                    "factor": 0.00003
                }
            },
            "Train": {
                "dataset": {
                    "name": "SimpleDataSet",
                    "data_dir": "/opt/ml/input/data/training/",
                    "label_file_list": ["/opt/ml/input/data/training/rec_gt_train.txt"],
                    "transforms": [
                        {"DecodeImage": {"img_mode": "BGR", "channel_first": False}},
                        {"CTCLabelEncode": {}},
                        {"RecResizeImg": {"image_shape": [3, 32, 100]}},  # ลดขนาดภาพ
                        {"KeepKeys": {"keep_keys": ["image", "label", "length"]}}
                    ]
                },
                "loader": {
                    "shuffle": True,
                    "batch_size_per_card": 256,  # เพิ่ม batch size
                    "drop_last": True,
                    "num_workers": 4
                }
            },
            "Eval": {
                "dataset": {
                    "name": "SimpleDataSet", 
                    "data_dir": "/opt/ml/input/data/training/",
                    "label_file_list": ["/opt/ml/input/data/training/rec_gt_val.txt"],
                    "transforms": [
                        {"DecodeImage": {"img_mode": "BGR", "channel_first": False}},
                        {"CTCLabelEncode": {}},
                        {"RecResizeImg": {"image_shape": [3, 32, 100]}},
                        {"KeepKeys": {"keep_keys": ["image", "label", "length"]}}
                    ]
                },
                "loader": {
                    "shuffle": False,
                    "batch_size_per_card": 256,
                    "drop_last": False,
                    "num_workers": 4
                }
            }
        }
        
        # บันทึก config
        config_path = self.project_root / f"configs/rec/single_char_{self.timestamp}.yml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
        self.logger.info(f"✅ สร้าง single char config: {config_path}")
        return config_path

    def step_3_start_training(self, s3_bucket, s3_prefix, config_path):
        """🚀 Step 3: เริ่มการเทรน single character บน SageMaker"""
        self.logger.info("🎯 Step 3: เริ่มการเทรน Single Character บน SageMaker")
        
        sagemaker = boto3.client('sagemaker', region_name='ap-southeast-1')
        
        job_name = f"thai-single-char-{self.timestamp}"
        
        training_job_params = {
            'TrainingJobName': job_name,
            'AlgorithmSpecification': {
                'TrainingImage': '484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:latest',
                'TrainingInputMode': 'File'
            },
            'RoleArn': 'arn:aws:iam::484468818942:role/paddleocr-dev-sagemaker-role',
            'InputDataConfig': [{
                'ChannelName': 'training',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': f's3://{s3_bucket}/{s3_prefix}/',
                        'S3DataDistributionType': 'FullyReplicated'
                    }
                }
            }],
            'OutputDataConfig': {
                'S3OutputPath': f's3://{s3_bucket}/models/'
            },
            'ResourceConfig': {
                'InstanceType': 'ml.m5.large',
                'InstanceCount': 1,
                'VolumeSizeInGB': 30
            },
            'StoppingCondition': {
                'MaxRuntimeInSeconds': 10800  # 3 ชั่วโมง
            },
            'HyperParameters': {
                'epochs': '100',
                'batch-size': '256',
                'learning-rate': '0.0005',
                'max-text-length': '1',
                'config': config_path.name
            }
        }
        
        response = sagemaker.create_training_job(**training_job_params)
        
        self.logger.info(f"✅ เริ่มการเทรน Single Character แล้ว: {job_name}")
        self.logger.info(f"📍 Job ARN: {response['TrainingJobArn']}")
        
        return job_name

    def step_4_monitor_training(self, job_name):
        """📊 Step 4: ติดตามการเทรน"""
        self.logger.info("🎯 Step 4: ติดตามการเทรน Single Character")
        
        sagemaker = boto3.client('sagemaker', region_name='ap-southeast-1')
        
        import time
        start_time = time.time()
        
        while True:
            response = sagemaker.describe_training_job(TrainingJobName=job_name)
            status = response['TrainingJobStatus']
            
            elapsed = int(time.time() - start_time)
            elapsed_str = f"{elapsed//3600:02d}:{(elapsed%3600)//60:02d}:{elapsed%60:02d}"
            
            self.logger.info(f"📊 สถานะ: {status} | เวลาที่ผ่านไป: {elapsed_str}")
            
            if status in ['Completed', 'Failed', 'Stopped']:
                break
                
            time.sleep(60)  # รอ 1 นาที
            
        if status == 'Completed':
            self.logger.info("🎉 การเทรน Single Character เสร็จสิ้น!")
            return response['ModelArtifacts']['S3ModelArtifacts']
        else:
            raise Exception(f"❌ การเทรนล้มเหลว: {status}")

    def step_5_download_model(self, model_s3_path):
        """📥 Step 5: ดาวน์โหลดโมเดล single character"""
        self.logger.info("🎯 Step 5: ดาวน์โหลดโมเดล Single Character")
        
        # สร้าง directory สำหรับโมเดลใหม่
        model_dir = self.project_root / f"models/single_char_{self.timestamp}"
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # ดาวน์โหลดจาก S3
        cmd = [
            "aws", "s3", "cp", 
            model_s3_path,
            str(model_dir / "model.tar.gz")
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"❌ ดาวน์โหลดล้มเหลว: {result.stderr}")
            
        # แตกไฟล์
        import tarfile
        with tarfile.open(model_dir / "model.tar.gz", 'r:gz') as tar:
            tar.extractall(model_dir)
            
        self.logger.info(f"✅ ดาวน์โหลดโมเดล Single Character แล้ว: {model_dir}")
        return model_dir

    def step_6_test_single_char_model(self, model_dir):
        """🧪 Step 6: ทดสอบโมเดล single character"""
        self.logger.info("🎯 Step 6: ทดสอบโมเดล Single Character")
        
        # สร้าง inference config สำหรับ single character
        inference_config = {
            "Global": {
                "use_gpu": False,
                "pretrained_model": str(model_dir / "best_accuracy"),
                "character_dict_path": str(self.project_root / "thai-letters/th_dict.txt"),
                "character_type": "thai",
                "max_text_length": 1,  # SINGLE CHARACTER
                "infer_mode": True,
                "use_space_char": False
            },
            "Architecture": {
                "model_type": "rec",
                "algorithm": "CRNN",
                "Backbone": {
                    "name": "MobileNetV3",
                    "scale": 0.5,
                    "model_name": "large"
                },
                "Neck": {
                    "name": "SequenceEncoder",
                    "encoder_type": "rnn",
                    "hidden_size": 48
                },
                "Head": {
                    "name": "CTCHead",
                    "fc_decay": 0.00001
                }
            },
            "PostProcess": {"name": "CTCLabelDecode"}
        }
        
        # บันทึก config
        inference_config_path = model_dir / "single_char_inference_config.yml"
        with open(inference_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(inference_config, f, default_flow_style=False, allow_unicode=True)
            
        # ทดสอบด้วยภาพตัวอย่าง
        test_images_dir = self.project_root / "test_images"
        if test_images_dir.exists():
            test_images = list(test_images_dir.glob("*.jpg"))[:10]
            
            self.logger.info(f"🧪 ทดสอบ Single Character กับ {len(test_images)} ภาพ")
            
            results = []
            for img_path in test_images:
                cmd = [
                    "python", "PaddleOCR/tools/infer_rec.py",
                    "-c", str(inference_config_path),
                    "-o", f"Global.infer_img={img_path}"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.project_root))
                
                if "result:" in result.stdout:
                    prediction = result.stdout.split("result:")[1].split("\n")[0].strip()
                    # สำหรับ single char เอาแค่ตัวแรก
                    if prediction:
                        single_char = prediction.split()[0] if ' ' in prediction else prediction[:1]
                        results.append({
                            "image": img_path.name,
                            "prediction": single_char,
                            "raw": prediction
                        })
                        self.logger.info(f"📷 {img_path.name}: '{single_char}'")
                    
            # สรุปผลลัพธ์
            self.logger.info(f"✅ ทดสอบ Single Character เสร็จสิ้น: {len(results)} ผลลัพธ์")
            
            # บันทึกผลลัพธ์
            results_file = model_dir / "test_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                
            return results

    def run_complete_workflow(self):
        """🎯 รันทั้งหมดแบบ One-Click สำหรับ Single Character"""
        try:
            self.logger.info("🚀 เริ่มต้น Easy Thai OCR Single Character Training Workflow")
            
            # Step 1: เตรียมข้อมูล single character
            s3_bucket, s3_prefix = self.step_1_prepare_single_char_data()
            
            # Step 2: สร้าง single char config
            config_path = self.step_2_create_single_char_config()
            
            # Step 3: เริ่มการเทรน
            job_name = self.step_3_start_training(s3_bucket, s3_prefix, config_path)
            
            # Step 4: ติดตามการเทรน
            model_s3_path = self.step_4_monitor_training(job_name)
            
            # Step 5: ดาวน์โหลดโมเดล
            model_dir = self.step_5_download_model(model_s3_path)
            
            # Step 6: ทดสอบโมเดล single character
            test_results = self.step_6_test_single_char_model(model_dir)
            
            self.logger.info("🎉 สำเร็จ! โมเดล Thai OCR Single Character พร้อมใช้งาน")
            
            return {
                "status": "success",
                "job_name": job_name,
                "model_path": str(model_dir),
                "timestamp": self.timestamp,
                "test_results": test_results,
                "model_type": "single_character"
            }
            
        except Exception as e:
            self.logger.error(f"❌ เกิดข้อผิดพลาด: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": self.timestamp,
                "model_type": "single_character"
            }

def main():
    """Main function"""
    print("🎯 Easy Thai OCR Single Character Training")
    print("=" * 60)
    
    trainer = EasySingleCharTraining()
    result = trainer.run_complete_workflow()
    
    print(f"\n🎯 สรุปผลลัพธ์:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
