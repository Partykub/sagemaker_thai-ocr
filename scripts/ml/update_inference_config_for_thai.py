#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ปรับแต่ง Config สำหรับภาษาไทยเพื่อเพิ่ม Accuracy
"""

import yaml
import os
import shutil
from pathlib import Path

def update_thai_ocr_config():
    """ปรับแต่ง Config สำหรับภาษาไทยเพื่อเพิ่ม Accuracy"""
    
    config_path = 'models/sagemaker_trained/config_local.yml'
    new_config_path = 'models/sagemaker_trained/config_optimized.yml'
    
    if not os.path.exists(config_path):
        print(f"ไม่พบไฟล์ config ที่ {config_path}")
        return None
    
    # สำรองไฟล์เดิม
    backup_path = f"{config_path}.backup"
    if not os.path.exists(backup_path):
        shutil.copy2(config_path, backup_path)
        print(f"สำรองไฟล์เดิมไว้ที่: {backup_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("การตั้งค่าเดิม:")
    print(f"  max_text_length: {config.get('Global', {}).get('max_text_length', 'ไม่พบ')}")
    print(f"  character_dict_path: {config.get('Global', {}).get('character_dict_path', 'ไม่พบ')}")
    print(f"  use_space_char: {config.get('Global', {}).get('use_space_char', 'ไม่พบ')}")
    
    # ปรับแต่งค่า Config ที่สำคัญ
    if 'Global' not in config:
        config['Global'] = {}
    
    # ปรับค่าสำคัญ
    config['Global']['max_text_length'] = 5  # ลดจาก 25 เป็น 5
    config['Global']['character_dict_path'] = './thai-letters/th_dict_optimized.txt'
    config['Global']['use_space_char'] = False
    
    # ปรับแต่ง decoder parameters
    if 'PostProcess' not in config:
        config['PostProcess'] = {}
    
    config['PostProcess']['name'] = 'CTCLabelDecode'
    config['PostProcess']['use_space_char'] = False
    
    # เพิ่มการตรวจสอบความเชื่อมั่น
    if 'Metric' not in config:
        config['Metric'] = {}
    
    config['Metric']['name'] = 'RecMetric'
    config['Metric']['main_indicator'] = 'acc'
    
    # บันทึกไฟล์ config ใหม่
    with open(new_config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\n✅ สร้าง config ใหม่สำเร็จ: {new_config_path}")
    
    print("การตั้งค่าใหม่:")
    print(f"  max_text_length: {config['Global']['max_text_length']}")
    print(f"  character_dict_path: {config['Global']['character_dict_path']}")
    print(f"  use_space_char: {config['Global']['use_space_char']}")
    
    return new_config_path

if __name__ == "__main__":
    update_thai_ocr_config()
