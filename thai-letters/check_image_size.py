#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ตรวจสอบขนาดของรูปภาพที่สร้างขึ้น
"""

from PIL import Image
import os

# ตรวจสอบรูปภาพตัวอย่าง
image_folder = "datasets/raw/thai_dataset_minimal_1samples_number_dict_ideal_conditions_0806_1424/images"

if os.path.exists(image_folder):
    # ดูรูปภาพแรก
    first_image = os.path.join(image_folder, "000_00.jpg")
    if os.path.exists(first_image):
        img = Image.open(first_image)
        print(f"📐 ขนาดรูปภาพ: {img.size} (กว้าง x สูง)")
        print(f"📊 รูปแบบ: {img.format}")
        print(f"📝 โหมดสี: {img.mode}")
        
        # ตรวจสอบขนาดของรูปอื่นๆ
        print("\n🔍 ตรวจสอบรูปภาพทั้งหมด:")
        for filename in os.listdir(image_folder):
            if filename.endswith('.jpg'):
                img_path = os.path.join(image_folder, filename)
                img = Image.open(img_path)
                print(f"   {filename}: {img.size}")
    else:
        print("❌ ไม่พบรูปภาพตัวอย่าง")
else:
    print("❌ ไม่พบโฟลเดอร์รูปภาพ")
