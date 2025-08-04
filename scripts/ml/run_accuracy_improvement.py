#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
รันขั้นตอนทั้งหมดเพื่อเพิ่ม Accuracy ของ Thai OCR Model
"""

import os
import sys
import subprocess
from pathlib import Path

def run_accuracy_improvement_pipeline():
    """รันขั้นตอนทั้งหมดเพื่อเพิ่ม Accuracy"""
    
    print("🎯 เริ่มกระบวนการเพิ่ม Accuracy ของ Thai OCR Model")
    print("=" * 60)
    
    # ตรวจสอบว่าอยู่ใน project root
    if not os.path.exists('thai-letters/th_dict.txt'):
        print("❌ กรุณารันสคริปต์นี้ในโฟลเดอร์ root ของโปรเจค")
        return False
    
    steps = [
        {
            "name": "สร้าง Dictionary ที่เหมาะสม",
            "script": "scripts/ml/optimize_thai_dict.py",
            "description": "ลด dictionary จาก ~880 เป็น ~100 อักขระ"
        },
        {
            "name": "ปรับแต่ง Configuration",
            "script": "scripts/ml/update_inference_config_for_thai.py", 
            "description": "ตั้งค่า max_text_length=5, use_space_char=False"
        },
        {
            "name": "ทดสอบโมเดลที่ปรับแต่งแล้ว",
            "script": "scripts/ml/test_optimized_model.py",
            "description": "ทดสอบกับรูปภาพเดิมและวิเคราะห์ผลลัพธ์"
        }
    ]
    
    results = []
    
    for i, step in enumerate(steps, 1):
        print(f"\n📋 ขั้นตอนที่ {i}: {step['name']}")
        print(f"   {step['description']}")
        print(f"   กำลังรัน: {step['script']}")
        
        try:
            # รันสคริปต์
            result = subprocess.run([
                sys.executable, step['script']
            ], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print(f"   ✅ สำเร็จ")
                if result.stdout:
                    # แสดงเฉพาะบรรทัดสำคัญ
                    for line in result.stdout.split('\n'):
                        if any(keyword in line for keyword in ['✅', '📊', '🎯', 'สำเร็จ', 'จำนวน']):
                            print(f"   {line}")
                results.append({"step": step['name'], "status": "success", "output": result.stdout})
            else:
                print(f"   ❌ ล้มเหลว")
                if result.stderr:
                    print(f"   ข้อผิดพลาด: {result.stderr}")
                results.append({"step": step['name'], "status": "failed", "error": result.stderr})
                
        except Exception as e:
            print(f"   ❌ เกิดข้อผิดพลาด: {e}")
            results.append({"step": step['name'], "status": "error", "error": str(e)})
    
    # สรุปผลลัพธ์
    print("\n" + "=" * 60)
    print("📊 สรุปผลการดำเนินการ")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    total_steps = len(steps)
    
    for result in results:
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_icon} {result['step']}")
    
    print(f"\nความสำเร็จ: {success_count}/{total_steps} ขั้นตอน")
    
    if success_count == total_steps:
        print("\n🎉 การปรับปรุง Accuracy เสร็จสิ้น!")
        print("📁 ไฟล์ที่สร้างขึ้น:")
        print("   - thai-letters/th_dict_optimized.txt")
        print("   - models/sagemaker_trained/config_optimized.yml")
        print("   - OPTIMIZED_MODEL_TEST_RESULTS_[timestamp].json")
        print("\n📈 ตรวจสอบผลลัพธ์ในไฟล์ JSON เพื่อดู accuracy ที่ปรับปรุงแล้ว")
    else:
        print(f"\n⚠️  มีขั้นตอนที่ล้มเหลว {total_steps - success_count} ขั้นตอน")
        print("กรุณาตรวจสอบข้อผิดพลาดด้านบนและแก้ไข")
    
    return success_count == total_steps

if __name__ == "__main__":
    run_accuracy_improvement_pipeline()
