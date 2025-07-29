#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized Thai Character Dataset Generator
สร้าง dataset ที่มีอุปสรรคเหมาะสม ไม่เยอะเกินไปจนมองไม่เห็นตัวอักษร
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import json
import random
import argparse
from datetime import datetime

class OptimizedThaiGenerator:
    def __init__(self, output_dir="thai_dataset_production", samples_per_char=10):
        self.output_dir = output_dir
        self.samples_per_char = samples_per_char
        self.image_size = (128, 64)
        
        # ฟอนต์และขนาด
        self.font_path = self._find_tahoma_font()
        self.font_sizes = [44, 48, 52, 56]
        
        # อุปสรรคที่เหมาะสม (ลดจาก 15 เหลือ 8 ประเภท)
        self.obstacles = {
            # การหมุนเล็กน้อย (ลดลง)
            'rotation': [-2, -1, 0, 1, 2],
            
            # ความสว่าง (ลดช่วง)
            'brightness': [0.8, 0.9, 1.0, 1.1, 1.2],
            
            # ความคมชัด (ลดช่วง)
            'contrast': [0.8, 0.9, 1.0, 1.1, 1.2],
            
            # การเบลอเล็กน้อย (ลดลง)
            'blur': [0, 0.2, 0.4],
            
            # สัญญาณรบกวนน้อย (ลดลง)
            'noise_level': [0, 0.02, 0.05],
            
            # ตำแหน่ง (เฉพาะกลางๆ)
            'position': ['center-left', 'center', 'center-right'],
            
            # ระยะห่าง
            'padding': [15, 20, 25],
            
            # การบีบอัดคุณภาพดี (เฉพาะคุณภาพสูง)
            'compression': [85, 90, 95, 100]
        }
        
        # สถิติ
        self.stats = {
            "total_characters": 0,
            "samples_per_char": samples_per_char,
            "total_generated": 0,
            "successful": 0,
            "failed": 0,
            "obstacles_applied": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # สร้างโฟลเดอร์
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)
        
    def _find_tahoma_font(self):
        """ค้นหา Tahoma font"""
        paths = [
            "C:/Windows/Fonts/tahoma.ttf",
            "C:/Windows/Fonts/Tahoma.ttf",
            "/System/Library/Fonts/Tahoma.ttf",
        ]
        
        for path in paths:
            if os.path.exists(path):
                return path
        return None
        
    def _load_characters(self, dict_path):
        """อ่านตัวอักษรจากไฟล์"""
        characters = []
        with open(dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                char = line.strip()
                if char and char not in ['', ' ', '\n']:
                    characters.append(char)
        
        # กรองเอาเฉพาะตัวอักษรที่สามารถแสดงผลได้
        valid_chars = []
        for char in characters:
            if self._can_render_character(char):
                valid_chars.append(char)
        
        print(f"📖 Valid characters: {len(valid_chars)}/{len(characters)}")
        return valid_chars
        
    def _can_render_character(self, char):
        """ตรวจสอบว่าตัวอักษรสามารถแสดงผลได้หรือไม่"""
        try:
            test_img = Image.new('RGB', (64, 32), (255, 255, 255))
            draw = ImageDraw.Draw(test_img)
            
            if self.font_path:
                font = ImageFont.truetype(self.font_path, 24)
            else:
                font = ImageFont.load_default()
                
            draw.text((10, 5), char, fill=(0, 0, 0), font=font)
            
            array = np.array(test_img)
            gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
            return not np.all(gray == 255)
            
        except:
            return False
            
    def _random_obstacles(self):
        """สุ่มเลือกอุปสรรคต่างๆ แบบเหมาะสม"""
        selected = {}
        for obstacle_type, options in self.obstacles.items():
            selected[obstacle_type] = random.choice(options)
            
            # นับสถิติการใช้อุปสรรค
            if obstacle_type not in self.stats["obstacles_applied"]:
                self.stats["obstacles_applied"][obstacle_type] = {}
            obstacle_value = str(selected[obstacle_type])
            if obstacle_value not in self.stats["obstacles_applied"][obstacle_type]:
                self.stats["obstacles_applied"][obstacle_type][obstacle_value] = 0
            self.stats["obstacles_applied"][obstacle_type][obstacle_value] += 1
            
        return selected
        
    def generate_character_variations(self, char, char_index):
        """สร้างภาพหลายแบบสำหรับตัวอักษรหนึ่งตัว"""
        variations = []
        
        for sample_idx in range(self.samples_per_char):
            try:
                # สุ่มเลือกอุปสรรค
                obstacles = self._random_obstacles()
                
                # สร้างภาพ
                img = self._create_optimized_image(char, obstacles)
                
                if img is not None:
                    # บันทึกภาพ
                    filename = f"{char_index:03d}_{sample_idx:02d}.jpg"
                    filepath = os.path.join(self.output_dir, "images", filename)
                    
                    # ปรับคุณภาพการบีบอัด
                    quality = obstacles['compression']
                    img.save(filepath, 'JPEG', quality=quality)
                    
                    variations.append({
                        "filename": filename,
                        "character": char,
                        "sample_index": sample_idx,
                        "obstacles": obstacles
                    })
                    
                    self.stats["successful"] += 1
                else:
                    self.stats["failed"] += 1
                    
            except Exception as e:
                print(f"❌ Error creating variation {sample_idx} for '{char}': {e}")
                self.stats["failed"] += 1
                
        return variations
        
    def _create_optimized_image(self, char, obstacles):
        """สร้างภาพที่มีอุปสรรคเหมาะสม ไม่มากเกินไป"""
        try:
            # สร้างภาพพื้นหลังสีขาว
            img = Image.new('RGB', self.image_size, (255, 255, 255))
            
            # โหลดฟอนต์
            font_size = random.choice(self.font_sizes)
            if self.font_path:
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                font = ImageFont.load_default()
                
            draw = ImageDraw.Draw(img)
            
            # คำนวณขนาดตัวอักษร
            bbox = draw.textbbox((0, 0), char, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # คำนวณตำแหน่ง
            padding = obstacles['padding']
            position = obstacles['position']
            
            if 'left' in position:
                x = padding
            elif 'right' in position:
                x = self.image_size[0] - text_width - padding
            else:  # center
                x = (self.image_size[0] - text_width) // 2
                
            y = (self.image_size[1] - text_height) // 2
            
            # วาดตัวอักษร
            draw.text((x, y), char, fill=(0, 0, 0), font=font)
            
            # แปลงเป็น numpy array สำหรับการปรับแต่ง
            img_array = np.array(img)
            
            # ใช้ transformation ที่เหมาะสม
            img_array = self._apply_gentle_transformations(img_array, obstacles)
            
            # กลับเป็น PIL Image
            img = Image.fromarray(img_array)
            
            # ตรวจสอบว่าภาพมีเนื้อหา
            if self._is_image_valid(img):
                return img
            else:
                return None
                
        except Exception as e:
            print(f"Error creating optimized image: {e}")
            return None
            
    def _apply_gentle_transformations(self, img_array, obstacles):
        """ใช้การแปลงที่อ่อนโยน ไม่รุนแรงจนเกินไป"""
        
        # การหมุนเล็กน้อย
        if obstacles['rotation'] != 0:
            center = (img_array.shape[1] // 2, img_array.shape[0] // 2)
            matrix = cv2.getRotationMatrix2D(center, obstacles['rotation'], 1.0)
            img_array = cv2.warpAffine(img_array, matrix, (img_array.shape[1], img_array.shape[0]), 
                                     borderValue=(255, 255, 255))
        
        # ปรับความสว่าง (อ่อนโยน)
        if obstacles['brightness'] != 1.0:
            img_array = img_array.astype(np.float32)
            img_array *= obstacles['brightness']
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        # ปรับ contrast (อ่อนโยน)
        if obstacles['contrast'] != 1.0:
            img_array = img_array.astype(np.float32)
            img_array = ((img_array - 128) * obstacles['contrast'] + 128)
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        # เพิ่ม noise เล็กน้อย
        if obstacles['noise_level'] > 0:
            noise = np.random.normal(0, obstacles['noise_level'] * 255, img_array.shape)
            img_array = img_array.astype(np.float32) + noise
            img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        
        # เบลอเล็กน้อย
        if obstacles['blur'] > 0:
            kernel_size = int(obstacles['blur'] * 4) + 1
            if kernel_size % 2 == 0:
                kernel_size += 1
            if kernel_size >= 3:  # เฉพาะเมื่อ kernel ใหญ่พอ
                img_array = cv2.GaussianBlur(img_array, (kernel_size, kernel_size), 0)
        
        return img_array
        
    def _is_image_valid(self, img):
        """ตรวจสอบว่าภาพมีเนื้อหาและมองเห็นได้"""
        img_array = np.array(img)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # ตรวจสอบว่ามีพิกเซลที่ไม่ใช่สีขาว
        non_white_pixels = np.sum(gray < 240)
        
        # ตรวจสอบว่าตัวอักษรยังมองเห็นได้ (ไม่เบลอหรือจางเกินไป)
        edges = cv2.Canny(gray, 50, 150)
        edge_pixels = np.sum(edges > 0)
        
        return non_white_pixels > 50 and edge_pixels > 20
        
    def generate_optimized_dataset(self, dict_path):
        """สร้าง optimized dataset"""
        print("🚀 Starting Optimized Thai Dataset Generation")
        print(f"📁 Output: {self.output_dir}")
        print(f"🔢 Samples per character: {self.samples_per_char}")
        print(f"🎯 Optimized obstacles: {len(self.obstacles)} types (reduced from 15)")
        print("=" * 60)
        
        # แสดงรายการอุปสรรคที่เหมาะสม
        print("🎨 Optimized Obstacles (Character-Friendly):")
        for i, (obstacle_type, options) in enumerate(self.obstacles.items(), 1):
            print(f"  {i:2d}. {obstacle_type}: {len(options)} options")
        print("=" * 60)
        
        # อ่านตัวอักษร
        characters = self._load_characters(dict_path)
        self.stats["total_characters"] = len(characters)
        self.stats["total_generated"] = len(characters) * self.samples_per_char
        
        # สร้างไฟล์ labels
        labels_file = os.path.join(self.output_dir, "labels.txt")
        all_variations = []
        
        with open(labels_file, 'w', encoding='utf-8') as f:
            for char_idx, char in enumerate(characters):
                print(f"📝 Generating {self.samples_per_char} variations for '{char}' ({char_idx+1}/{len(characters)})")
                
                # สร้างภาพหลายแบบ
                variations = self.generate_character_variations(char, char_idx)
                all_variations.extend(variations)
                
                # เขียน labels
                for var in variations:
                    f.write(f"{var['filename']}\t{var['character']}\n")
                
                # แสดงความคืบหน้า
                if (char_idx + 1) % 50 == 0:
                    success_rate = (self.stats["successful"] / ((char_idx + 1) * self.samples_per_char) * 100)
                    print(f"✅ Progress: {char_idx+1}/{len(characters)} chars | Success rate: {success_rate:.1f}%")
        
        # บันทึกข้อมูลรายละเอียด
        details_file = os.path.join(self.output_dir, "dataset_details.json")
        with open(details_file, 'w', encoding='utf-8') as f:
            json.dump({
                "stats": self.stats,
                "variations": all_variations,
                "configuration": {
                    "samples_per_char": self.samples_per_char,
                    "image_size": self.image_size,
                    "font_sizes": self.font_sizes,
                    "obstacles": self.obstacles,
                    "optimization": "Character-friendly, reduced obstacles"
                }
            }, f, ensure_ascii=False, indent=2)
        
        # แสดงสรุป
        self._print_summary(characters)
        
    def _print_summary(self, characters):
        """แสดงสรุปผล"""
        print("\n" + "=" * 60)
        print("📊 OPTIMIZED DATASET SUMMARY")
        print("=" * 60)
        print(f"🔤 Total characters: {len(characters)}")
        print(f"🎯 Samples per character: {self.samples_per_char}")
        print(f"📊 Target total images: {len(characters) * self.samples_per_char}")
        print(f"✅ Successfully generated: {self.stats['successful']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"📈 Success rate: {(self.stats['successful']/(len(characters) * self.samples_per_char)*100):.1f}%")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🎨 Obstacles: Optimized for readability")
        print(f"👁️  Character visibility: Enhanced")
        print("=" * 60)

def main():
    """ฟังก์ชันหลักที่รับ arguments"""
    parser = argparse.ArgumentParser(description='Optimized Thai Character Dataset Generator')
    parser.add_argument('samples', type=int, 
                       help='Number of samples per character (required)')
    parser.add_argument('-d', '--dict', default='th_dict.txt', 
                       help='Path to character dictionary file (default: th_dict.txt)')
    parser.add_argument('-o', '--output', default=None,
                       help='Output directory (default: auto-generated)')
    parser.add_argument('--show-obstacles', action='store_true',
                       help='Show optimized obstacles and exit')
    
    args = parser.parse_args()
    
    # แสดงรายการอุปสรรคหากต้องการ
    if args.show_obstacles:
        generator = OptimizedThaiGenerator()
        print("🎨 Optimized Obstacles (Character-Friendly):")
        for i, (obstacle_type, options) in enumerate(generator.obstacles.items(), 1):
            print(f"{i:2d}. {obstacle_type}:")
            print(f"    Options: {options}")
            print()
        return
    
    # สร้างชื่อ output directory อัตโนมัติ
    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        args.output = f"thai_dataset_{args.samples}samples_{timestamp}"
    
    print(f"🎯 Creating optimized dataset: {args.samples} samples per character")
    print(f"📖 Dictionary: {args.dict}")
    print(f"📁 Output: {args.output}")
    print(f"👁️  Optimization: Character visibility enhanced")
    
    # สร้าง generator
    generator = OptimizedThaiGenerator(args.output, args.samples)
    
    # สร้าง dataset
    generator.generate_optimized_dataset(args.dict)
    
    print(f"\n🎉 Optimized dataset completed!")
    print(f"📁 Images: {args.output}/images/")
    print(f"📄 Labels: {args.output}/labels.txt")
    print(f"📋 Details: {args.output}/dataset_details.json")

if __name__ == "__main__":
    main()
