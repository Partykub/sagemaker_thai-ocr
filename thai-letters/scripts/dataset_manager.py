#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Thai Dataset Manager - จัดการโครงสร้าง datasets แบบเป็นระเบียบ

จัดการโครงสร้าง dataset ตามมาตรฐาน:
thai-letters/
├── datasets/                    # 🎯 โฟลเดอร์เก็บ datasets ทั้งหมด
│   ├── raw/                     # Dataset ดิบที่สร้างใหม่
│   ├── converted/               # Dataset ที่แปลงเป็น PaddleOCR format แล้ว
│   └── samples/                 # Dataset ตัวอย่างขนาดเล็ก
└── scripts/                     # Scripts จัดการ dataset
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class ThaiDatasetManager:
    """จัดการโครงสร้าง dataset แบบเป็นระเบียบ"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize dataset manager"""
        if base_dir is None:
            # Get thai-letters directory (parent of scripts directory)
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
            
        # Dataset directories
        self.datasets_dir = self.base_dir / "datasets"
        self.raw_dir = self.datasets_dir / "raw"
        self.converted_dir = self.datasets_dir / "converted"
        self.samples_dir = self.datasets_dir / "samples"
        
    def ensure_structure(self):
        """สร้างโครงสร้าง directory ที่จำเป็น"""
        directories = [
            self.datasets_dir,
            self.raw_dir,
            self.converted_dir, 
            self.samples_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_output_path(self, dataset_type: str = "converted", custom_name: str = None) -> str:
        """
        ได้ path สำหรับเก็บ dataset ใหม่
        
        Args:
            dataset_type: ประเภท dataset ('raw', 'converted', 'samples')
            custom_name: ชื่อ dataset ที่ต้องการ (ถ้าไม่ระบุจะสร้างอัตโนมัติ)
            
        Returns:
            Path string สำหรับเก็บ dataset
        """
        self.ensure_structure()
        
        if dataset_type == "raw":
            target_dir = self.raw_dir
            prefix = "thai_dataset_raw"
        elif dataset_type == "samples":
            target_dir = self.samples_dir
            prefix = "thai_dataset_sample"
        else:  # converted (default)
            target_dir = self.converted_dir
            prefix = "train_data_thai_paddleocr"
        
        if custom_name:
            output_name = custom_name
        else:
            timestamp = datetime.now().strftime("%m%d_%H%M")
            output_name = f"{prefix}_{timestamp}"
        
        return str(target_dir / output_name)