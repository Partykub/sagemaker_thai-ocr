#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
สร้าง Thai Dictionary ที่เหมาะสมสำหรับ OCR โดยลดความซับซ้อนและเก็บเฉพาะอักขระที่จำเป็น
"""

import os
from pathlib import Path

def create_optimized_thai_dictionary():
    """สร้าง dictionary ที่เหมาะสมสำหรับภาษาไทยโดยเก็บรูปแบบผสมที่สำคัญ"""
    
    # 1. โหลด dictionary เดิม
    original_dict_path = 'thai-letters/th_dict.txt'
    if not os.path.exists(original_dict_path):
        print(f"ไม่พบไฟล์ {original_dict_path}")
        return None
        
    with open(original_dict_path, 'r', encoding='utf-8') as f:
        original_chars = [line.strip() for line in f if line.strip()]
    
    print(f"จำนวนอักขระในไฟล์เดิม: {len(original_chars)}")
    
    # 2. แยกประเภทของอักขระ
    thai_only_chars = []
    latin_chars = []
    numbers = []
    symbols = []
    combined_chars = []
    
    for char in original_chars:
        if len(char) == 1:
            # ตรวจสอบว่าเป็นอักษรไทยหรือไม่
            if '\u0E00' <= char <= '\u0E7F':  # Unicode range สำหรับอักษรไทย
                thai_only_chars.append(char)
            elif 'a' <= char.lower() <= 'z':
                latin_chars.append(char)
            elif '0' <= char <= '9':
                numbers.append(char)
            else:
                symbols.append(char)
        else:
            # อักขระไทยผสม (เช็คว่ามีอักขระไทยอย่างน้อย 1 ตัว)
            has_thai = any('\u0E00' <= c <= '\u0E7F' for c in char)
            if has_thai:
                combined_chars.append(char)
    
    print(f"อักขระไทยเดี่ยว: {len(thai_only_chars)}")
    print(f"อักขระละติน: {len(latin_chars)}")
    print(f"ตัวเลข: {len(numbers)}")
    print(f"สัญลักษณ์: {len(symbols)}")
    print(f"อักขระไทยผสม: {len(combined_chars)}")
    
    # 3. เลือกเฉพาะอักขระที่จำเป็น
    # - เก็บอักขระไทยทั้งหมด
    # - เก็บตัวเลข 0-9 (ตัวเลขอารบิก)
    # - เก็บเฉพาะอักขระผสมที่เป็น 1 ตัวอักษร (ไม่เอาอักขระผสม)
    
    important_combined = []  # ไม่เอาอักขระผสมเลย เพื่อลดความซับซ้อน
    
    # เพิ่มตัวเลขไทยถ้าไม่มี
    thai_numbers = ['๐', '๑', '๒', '๓', '๔', '๕', '๖', '๗', '๘', '๙']
    for num in thai_numbers:
        if num not in thai_only_chars:
            thai_only_chars.append(num)
    
    # 4. สร้าง dictionary ใหม่
    optimized_dict = (
        thai_only_chars + 
        ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] + 
        important_combined
    )
    
    # ลบ duplicates และเรียงลำดับ
    optimized_dict = list(dict.fromkeys(optimized_dict))  # Remove duplicates while preserving order
    
    # 5. บันทึกไฟล์
    output_path = 'thai-letters/th_dict_optimized.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        for char in optimized_dict:
            f.write(char + '\n')
    
    print(f"\n✅ สร้าง Dictionary ที่เหมาะสมสำเร็จ: {output_path}")
    print(f"จำนวนอักขระไทยเดี่ยว: {len(thai_only_chars)}")
    print(f"จำนวนอักขระไทยผสม (≤3 ตัว): {len(important_combined)}")
    print(f"จำนวนอักขระทั้งหมดในไฟล์ใหม่: {len(optimized_dict)}")
    print(f"ลดลงจากเดิม: {len(original_chars) - len(optimized_dict)} อักขระ ({(len(original_chars) - len(optimized_dict))/len(original_chars)*100:.1f}%)")
    
    # 6. แสดงตัวอย่างอักขระที่เก็บไว้
    print(f"\nตัวอย่างอักขระไทยเดี่ยว (10 ตัวแรก): {thai_only_chars[:10]}")
    print(f"ตัวอย่างอักขระผสม (10 ตัวแรก): {important_combined[:10]}")
    
    # 7. แสดงอักขระที่ถูกลบออก
    removed_chars = [c for c in original_chars if c not in optimized_dict]
    print(f"\nตัวอย่างอักขระที่ถูกลบออก (10 ตัวแรก): {removed_chars[:10]}")
    
    return output_path

if __name__ == "__main__":
    create_optimized_thai_dictionary()
