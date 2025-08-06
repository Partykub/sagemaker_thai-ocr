# Thai OCR Dataset Generator (Enhanced)

## 📋 Overview
สคริปต์ `thai_dataset_quick.py` เป็นเครื่องมือสร้าง dataset ภาษาไทยที่ได้รับการปรับปรุงใหม่ โดยมีฟีเจอร์การเลือก dictionary และเอฟเฟคต่างๆ พร้อมรูปภาพขนาดใหม่ที่เหมาะสำหรับ OCR

## 🎯 ฟีเจอร์หลัก

### � Dictionary Selection
- เลือกไฟล์ dictionary แบบ interactive
- รองรับไฟล์ที่ลงท้ายด้วย `_dict.txt`
- แสดงจำนวนตัวอักษรในแต่ละไฟล์

### 🎛️ Effects Selection (8 ประเภท)
1. **การหมุน (Rotation)**: -2 ถึง +2 องศา
2. **ความสว่าง (Brightness)**: 0.8-1.2
3. **ความคมชัด (Contrast)**: 0.8-1.2
4. **การเบลอ (Blur)**: 0-0.4
5. **สัญญาณรบกวน (Noise Level)**: 0-0.05
6. **ตำแหน่ง (Position)**: center-left, center, center-right
7. **ระยะห่าง (Padding)**: 15-25 พิกเซล
8. **การบีบอัด (Compression)**: 85-100% คุณภาพ

### 📐 Enhanced Image Size
- **ใหม่**: `128 x 96` pixels (+50% ความสูง)
- **ฟอนต์ใหม่**: 42-84 pixels (เพิ่มขนาดใหญ่สุด)
- เหมาะสำหรับตัวอักษรไทยที่มีเครื่องหมายวรรณยุกต์

## 🚀 วิธีใช้งาน

```bash
# เข้าโฟลเดอร์ thai-letters
cd thai-letters

# รันสคริปต์
python thai_dataset_quick.py <จำนวนตัวอย่าง>
```

### ตัวอย่างการใช้งาน

```bash
# ทดสอบเร็ว
python thai_dataset_quick.py 1

# มาตรฐาน (แนะนำ)
python thai_dataset_quick.py 10

# คุณภาพสูง
python thai_dataset_quick.py 20

# สำหรับ production
python thai_dataset_quick.py 50
```

## 🎛️ ตัวเลือกการใช้งาน

### 📚 การเลือก Dictionary:
```
📚 เลือกไฟล์ Dictionary:
----------------------------------------
  1. number_dict.txt (11 characters)
  2. th_dict.txt (881 characters)
----------------------------------------
กรุณาเลือก (1-2): 1
✅ เลือก: number_dict.txt
```

### 🎨 การเลือกเอฟเฟค:
```
🎛️ เลือกเอฟเฟค/อุปสรรคที่ต้องการ:
============================================================
  1. การหมุน (rotation)
  2. ความสว่าง (brightness)
  3. ความคมชัด (contrast)
  4. การเบลอ (blur)
  5. สัญญาณรบกวน (noise_level)
  6. ตำแหน่ง (position)
  7. ระยะห่าง (padding)
  8. การบีบอัด (compression)
  
  9. ✨ ใช้ทั้งหมด (แนะนำ)
  0. � ไม่ใช้เอฟเฟค (ภาพเปล่า)
------------------------------------------------------------
🎯 เลือกหมายเลข (คั่นด้วย , หากเลือกหลายตัว เช่น 1,2,3): 0
```

### 🎯 ตัวเลือกพิเศษ:
- **0**: ไม่ใช้เอฟเฟค (ภาพในอุดมคติ - ideal conditions)
- **9**: ✨ ใช้เอฟเฟคทั้งหมด (แนะนำ)
- **1,2,3**: เลือกเฉพาะเอฟเฟคที่ต้องการ

## 📁 ผลลัพธ์

### โครงสร้างไฟล์:
```
datasets/raw/thai_dataset_minimal_1samples_number_dict_ocr_focused_0806_1409/
├── images/                    # รูปภาพที่สร้าง
├── labels.txt                 # ป้ายกำกับ
└── dataset_details.json       # สถิติและรายละเอียด
```

### ตัวอย่างชื่อโฟลเดอร์:
- `thai_dataset_minimal_1samples_number_dict_ideal_conditions_0806_1424`
- `thai_dataset_minimal_1samples_number_dict_rot_brt_con_0806_1424`
- `thai_dataset_standard_10samples_th_dict_all_effects_0806_1424`

## � การปรับปรุงในเวอร์ชันนี้

### ✅ ฟีเจอร์ใหม่:
1. **Interactive Dictionary Selection**: เลือกไฟล์ dict แบบ interactive
2. **Flexible Effects Selection**: เลือกเอฟเฟคได้ตามต้องการ
3. **Enhanced Image Size**: เพิ่มความสูงจาก 64 เป็น 96 pixels (+50%)
4. **Improved Font Sizes**: เพิ่มขนาดฟอนต์ขึ้นถึง 84 pixels
5. **Better Output Naming**: ชื่อโฟลเดอร์บอกเอฟเฟคที่ใช้ได้ชัดเจน

### 🔧 การปรับปรุงระบบ:
- แก้ไขไฟล์เดิม `thai_dataset_quick.py` แทนการสร้างไฟล์ใหม่
- ลบไฟล์ v2 เพื่อไม่ให้สับสน
- เชื่อมต่อการเลือกเอฟเฟคกับ `thai_dataset_generator.py` สำเร็จ
- แก้ไขปัญหา "no effects" ที่ยังมีเอฟเฟคปรากฏ

## 🎓 คำแนะนำการใช้งาน

### สำหรับการทดสอบ:
```bash
python thai_dataset_quick.py 1     # เลือก dictionary → เลือก 0 (no effects)
```

### สำหรับการฝึกโมเดล:
```bash
python thai_dataset_quick.py 10    # เลือก dictionary → เลือก 9 (all effects)
```

### สำหรับการใช้งานเฉพาะ:
```bash
python thai_dataset_quick.py 5     # เลือก dictionary → เลือก 1,2,6 (rotation, brightness, position)
```

## 🔧 ข้อมูลทางเทคนิค

### ขนาดภาพที่ปรับปรุง:
- **เดิม**: 128 x 64 pixels (อัตราส่วน 2:1)
- **ใหม่**: 128 x 96 pixels (อัตราส่วน 4:3, +50% ความสูง)

### ขนาดฟอนต์ที่รองรับ:
- **เดิม**: 36-72 pixels
- **ใหม่**: 42-84 pixels (เพิ่มขนาดใหญ่สุด)

### ประโยชน์ของความสูงใหม่:
1. **👁️ อ่านง่ายขึ้น**: ตัวอักษรไทยมีพื้นที่มากขึ้นสำหรับเครื่องหมายวรรณยุกต์
2. **🔍 ความละเอียดดีขึ้น**: OCR สามารถแยกแยะรายละเอียดได้ดีกว่า
3. **📐 อัตราส่วนเหมาะสม**: 4:3 เหมาะสำหรับตัวอักษรไทยที่มีความสูง
4. **🚀 ประสิทธิภาพดีขึ้น**: รองรับฟอนต์ขนาดใหญ่ได้ดีกว่า

## 📋 สถานะการพัฒนา

### ✅ เสร็จสมบูรณ์:
- [x] Interactive dictionary selection
- [x] Flexible effects selection  
- [x] Enhanced image size (128x96)
- [x] Improved font size range
- [x] Better output folder naming
- [x] Effects parameter integration
- [x] "No effects" bug fix
- [x] File consolidation (removed v2)

### 🎯 การทดสอบ:
- [x] ทดสอบการเลือก dictionary สำเร็จ
- [x] ทดสอบการเลือกเอฟเฟคสำเร็จ
- [x] ทดสอบขนาดภาพใหม่สำเร็จ
- [x] ทดสอบการสร้างโฟลเดอร์สำเร็จ

---

สคริปต์นี้จะช่วยให้การสร้าง dataset มีความยืดหยุ่นและเหมาะสมกับการใช้งาน OCR ภาษาไทยมากขึ้น! 🚀
