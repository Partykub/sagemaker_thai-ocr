# 🚀 คู่มือการเทรนแบบ Advanced - เลือก Architecture และ GPU ได้

> **Updated**: 11 สิงหาคม 2025 - วิธีเทรนแบบละเอียดพร้อมทางเลือก architecture

## 📚 สารบัญ

1. [การเปรียบเทียบ Architecture](#1-การเปรียบเทียบ-architecture)
2. [การเลือก GPU และ Instance Type](#2-การเลือก-gpu-และ-instance-type)
3. [การเลือก Dataset สำหรับการเทรน](#3-การเลือก-dataset-สำหรับการเทรน)
4. [การเทรนแบบ Manual ทีละขั้นตอน](#4-การเทรนแบบ-manual-ทีละขั้นตอน)
5. [การเตรียม AWS สำหรับการเทรนครั้งใหม่](#5-การเตรียม-aws-สำหรับการเทรนครั้งใหม่)
6. [การปรับแต่ง Configuration ระดับสูง](#6-การปรับแต่ง-configuration-ระดับสูง)
7. [แนวทางการแก้ไขปัญหาที่พบบ่อย](#7-แนวทางการแก้ไขปัญหาที่พบบ่อย)
8. [สรุป: Best Practices](#8-สรุป-best-practices)
9. [ตัวอย่างคำสั่งเทรนและดาวน์โหลดโมเดล](#9-ตัวอย่างคำสั่งเทรนและดาวน์โหลดโมเดล)
10. [การวัดผลและประเมินโมเดล](#10-การวัดผลและประเมินโมเดล)

---

## 1. การเปรียบเทียบ Architecture

### Architecture Comparison Chart

| Architecture | Performance | Training Time | GPU Memory | Best Use Case | Complexity |
|--------------|-------------|--------------|------------|---------------|------------|
| **CRNN + MobileNetV3** | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐⭐<br>**Fast (13 min)** | ⭐⭐⭐⭐⭐<br>**Low** | Development<br>Numbers only<br>Quick PoC | Low |
| **SVTR_LCNet** | ⭐⭐⭐⭐⭐<br>**Best accuracy** | ⭐☆☆☆☆<br>**Slow (25+ hrs)** | ⭐⭐☆☆☆<br>**High** | Production<br>Full Thai text<br>Complex layouts | High |
| **SVTR** | ⭐⭐⭐⭐☆ | ⭐⭐☆☆☆<br>**Medium-Slow** | ⭐⭐⭐☆☆<br>**Medium-High** | Production<br>Complex cases<br>When accuracy is crucial | Medium-High |
| **SRN** | ⭐⭐⭐⭐☆ | ⭐⭐⭐☆☆<br>**Medium** | ⭐⭐⭐☆☆<br>**Medium** | Complex scripts<br>Curved text<br>Irregular placement | Medium |
| **SAR** | ⭐⭐⭐⭐☆ | ⭐⭐☆☆☆<br>**Medium-Slow** | ⭐⭐⭐☆☆<br>**Medium** | Attention-based<br>Complex scenes<br>Variable-length text | Medium-High |
| **RARE** | ⭐⭐⭐☆☆ | ⭐⭐⭐☆☆<br>**Medium** | ⭐⭐⭐⭐☆<br>**Medium-Low** | Irregular text<br>Curved text<br>Distorted scenes | Medium |
| **DB_MobileNetV3** | ⭐⭐⭐⭐☆ | ⭐⭐⭐☆☆<br>**Medium** | ⭐⭐⭐☆☆<br>**Medium** | Detection<br>Layout analysis<br>Table extraction | Medium |
| **NRTR** | ⭐⭐⭐⭐☆ | ⭐⭐☆☆☆<br>**Medium-Slow** | ⭐⭐☆☆☆<br>**High** | Transformer-based<br>Long sequences<br>Context-dependent text | High |
| **RobustScanner** | ⭐⭐⭐⭐☆ | ⭐⭐☆☆☆<br>**Medium-Slow** | ⭐⭐⭐☆☆<br>**Medium** | Challenging scenes<br>Noise resistance<br>Irregular text | Medium-High |

### วิธีเลือก Architecture

เลือก architecture ขึ้นอยู่กับความต้องการของโปรเจค:

| ความต้องการ | แนะนำให้ใช้ | ทางเลือกที่ดี |
|-----------|-----------|------------|
| เทรนเร็วที่สุด | CRNN + MobileNetV3 | RARE |
| ความแม่นยำสูงสุด | SVTR_LCNet | SVTR, NRTR |
| สมดุลทั้งความเร็วและความแม่นยำ | RARE, SRN | SAR, RobustScanner |
| ข้อความที่มีความซับซ้อนสูง | SVTR_LCNet, NRTR | SRN, SAR |
| ตัวอักษรภาษาไทยเต็มรูปแบบ | SVTR_LCNet | NRTR, SVTR |
| ประหยัดทรัพยากรที่สุด | CRNN + MobileNetV3 | RARE |
| ตัวเลขและตัวอักษรพื้นฐาน | CRNN + MobileNetV3 | RARE, SRN |
| การตรวจจับข้อความในภาพ | DB_MobileNetV3 | - |

### แนะนำ Architecture ตามกรณีใช้งาน

#### 1. CRNN + MobileNetV3 (Fast & Efficient)
**เหมาะสำหรับ**:
- ✅ การพัฒนาและทดสอบแนวคิด (13 นาที, $0.11)
- ✅ Dataset ขนาดเล็ก (น้อยกว่า 1,000 ภาพ)
- ✅ การรู้จำตัวเลขหรือตัวอักษรเดี่ยว
- ✅ กรณีมีงบประมาณจำกัด
- ✅ ขั้นตอนการทดสอบและตรวจสอบโครงสร้างพื้นฐาน

**ข้อดี**:
- 🔥 เทรนเร็วมาก (13 นาทีบน GPU)
- 💰 ประหยัดงบประมาณ ($0.11 ต่อการเทรน)
- 🧠 ใช้ GPU memory น้อย
- 🛠️ เข้าใจง่ายและปรับแต่งง่าย
- 📱 เหมาะสมสำหรับการใช้งานบน mobile

**ข้อเสีย**:
- ❌ ความแม่นยำต่ำกว่า SVTR_LCNet
- ❌ ไม่เหมาะกับข้อความซับซ้อน
- ❌ ข้อจำกัดในการจัดการกับตัวอักษรไทยที่มีสระบน/ล่าง

#### 2. SVTR_LCNet (High Accuracy)
**เหมาะสำหรับ**:
- ✅ โมเดลสำหรับ production
- ✅ Dataset ขนาดใหญ่ (มากกว่า 5,000 ภาพ)
- ✅ การรู้จำตัวอักษรไทยแบบเต็มรูปแบบ
- ✅ ต้องการความแม่นยำสูงสุด
- ✅ ใช้งานกับข้อความที่มีความซับซ้อน

**ข้อดี**:
- 🎯 ความแม่นยำสูง (state-of-the-art)
- 💼 รองรับข้อความซับซ้อน
- 🌟 ออกแบบสำหรับภาษาที่มีความซับซ้อนสูง (เช่น ไทย จีน)
- 🔍 ความสามารถในการจัดการกับข้อความที่มีความยาวต่างกัน
- 💪 ประสิทธิภาพดีในสภาพแวดล้อมที่มีความท้าทาย

**ข้อเสีย**:
- ⏱️ เทรนช้า (25+ ชั่วโมง)
- 💸 ค่าใช้จ่ายสูง ($25+ ต่อการเทรน)
- 🧠 ใช้ GPU memory มาก
- 🔄 ความซับซ้อนในการปรับแต่งพารามิเตอร์

#### 3. SVTR (Simplified Version)
**เหมาะสำหรับ**:
- ✅ การรู้จำข้อความไทยที่มีความซับซ้อน
- ✅ เมื่อต้องการสมดุลระหว่างความเร็วและความแม่นยำ
- ✅ ข้อความที่มีการจัดวางไม่เป็นระเบียบ

**ข้อดี**:
- 🔍 ใช้ vision transformer สำหรับการดึงคุณลักษณะที่ดีกว่า
- ⚡ เร็วกว่า SVTR_LCNet แต่ยังคงให้ความแม่นยำสูง
- 🌟 ประสิทธิภาพดีสำหรับภาษาไทย

**ข้อเสีย**:
- 🧠 ยังคงต้องการ GPU ที่มีประสิทธิภาพ
- ⚙️ ต้องการการปรับแต่งพารามิเตอร์

#### 4. SRN (Semantic Reasoning Network)
**เหมาะสำหรับ**:
- ✅ ข้อความที่มีการจัดวางผิดปกติ
- ✅ ตัวอักษรที่มีความคล้ายคลึงกันมาก
- ✅ ข้อความที่มีการบิดเบี้ยว

**ข้อดี**:
- 🧠 ใช้กลไกความสนใจ (attention mechanism)
- 🔄 รองรับข้อความที่มีการหมุนหรือบิดเบี้ยว
- 📊 ให้ผลลัพธ์ดีกับข้อความที่มีรูปแบบซับซ้อน

**ข้อเสีย**:
- ⏱️ เทรนช้ากว่า CRNN
- 🧩 ซับซ้อนในการปรับแต่ง

#### 5. DB_MobileNetV3 (Detection)
**เหมาะสำหรับ**:
- ✅ การตรวจจับข้อความในภาพ (text detection)
- ✅ การวิเคราะห์โครงสร้างเอกสาร
- ✅ การสกัดข้อมูลจากตาราง
- ✅ การระบุตำแหน่งข้อความก่อนการรู้จำ

**ข้อดี**:
- 📐 ค้นหาพื้นที่ข้อความได้ดี
- 📱 ประหยัด resource เมื่อใช้บน mobile
- 🔍 รองรับข้อความหลายทิศทาง
- 🔄 ทำงานได้ดีกับข้อความที่มีการหมุน
- 📑 เหมาะสำหรับการวิเคราะห์เอกสาร

**ข้อเสีย**:
- 🔢 ไม่สามารถรู้จำตัวอักษร (recognition) ได้เอง
- 🧩 ต้องใช้คู่กับโมเดล recognition
- 🎯 ไม่เหมาะสำหรับข้อความที่มีขนาดเล็กมาก

---

## 2. การเลือก GPU และ Instance Type

### AWS SageMaker Instance Types

| Instance Type | vCPUs | RAM | GPU | GPU Memory | Cost/Hour | Best For |
|---------------|-------|-----|-----|------------|-----------|----------|
| ml.g4dn.xlarge | 4 | 16 GB | 1x NVIDIA T4 | 16 GB | $0.526/hr | ⭐ **Best Value** |
| ml.g4dn.2xlarge | 8 | 32 GB | 1x NVIDIA T4 | 16 GB | $0.752/hr | Larger Datasets |
| ml.p3.2xlarge | 8 | 61 GB | 1x NVIDIA V100 | 16 GB | $3.06/hr | Faster Training |
| ml.g5.xlarge | 4 | 16 GB | 1x NVIDIA A10G | 24 GB | $1.006/hr | Larger Models |
| ml.m5.large | 2 | 8 GB | - | - | $0.115/hr | CPU Testing |

### การเลือก Instance Type ตามสถานการณ์

#### สำหรับ POC และการทดสอบ
- **แนะนำ**: `ml.g4dn.xlarge` (คุ้มค่าที่สุด)
- **Dataset**: < 1,000 ภาพ
- **เวลาเทรน**: 13-30 นาที
- **ค่าใช้จ่าย**: $0.11-$0.26
- **Architecture**: CRNN + MobileNetV3

#### สำหรับ Production Models
- **แนะนำ**: `ml.p3.2xlarge` (เร็วกว่า) หรือ `ml.g4dn.2xlarge` (ถูกกว่า)
- **Dataset**: > 5,000 ภาพ
- **เวลาเทรน**: 5-25 ชั่วโมง
- **ค่าใช้จ่าย**: $15-$76
- **Architecture**: SVTR_LCNet

#### สำหรับโมเดลซับซ้อนพิเศษ
- **แนะนำ**: `ml.g5.xlarge` (GPU memory สูง)
- **Dataset**: > 10,000 ภาพที่มีความซับซ้อนสูง
- **เวลาเทรน**: 10-30 ชั่วโมง
- **ค่าใช้จ่าย**: $10-$30
- **Architecture**: SVTR_LCNet ที่ปรับแต่งเป็นพิเศษ

---

## 3. การเลือก Dataset สำหรับการเทรน

### 3.1 ตารางเปรียบเทียบ Datasets

| Dataset | จำนวนไฟล์ | ประเภทข้อมูล | เหมาะกับ Architecture | การเทรน | ความแม่นยำที่ได้ |
|---------|----------|-----------|-------------------|---------|-------------|
| **train_data_thai_paddleocr_0807_1200** | 304 ไฟล์<br>(243 train, 61 val) | ตัวเลข 0-9 | CRNN+MobileNetV3 | 13 นาที<br>ml.g4dn.xlarge | 13.3% (baseline) |
| **train_data_thai_paddleocr_0804_1144** | 9,408 ไฟล์<br>(7,526 train, 1,882 val) | ตัวอักษรไทยเต็มรูปแบบ | SVTR_LCNet | 25+ ชั่วโมง<br>ml.p3.2xlarge | ยังไม่ทดสอบ |
| **train_data_thai_paddleocr_0805_1532** | 5,240 ไฟล์<br>(4,192 train, 1,048 val) | ผสมตัวเลขและตัวอักษรไทย | SVTR_LCNet<br>หรือ CRNN | 18+ ชั่วโมง<br>ml.g4dn.xlarge | ยังไม่ทดสอบ |
| **train_data_thai_paddleocr_0810_1630** | 12,560 ไฟล์<br>(10,048 train, 2,512 val) | ตัวอักษรไทยเต็มรูปแบบ + เอฟเฟกต์ | SVTR, NRTR, SRN | 30+ ชั่วโมง<br>ml.p3.2xlarge | ยังไม่ทดสอบ |
| **train_data_thai_paddleocr_0812_0945** | 6,320 ไฟล์<br>(5,056 train, 1,264 val) | ตัวอักษรไทยพื้นฐาน | SVTR_LCNet, SRN | 20+ ชั่วโมง<br>ml.g5.xlarge | ยังไม่ทดสอบ |

### 3.2 โครงสร้างข้อมูลที่ถูกต้อง
```
train_data_thai_paddleocr_*/
├── train_data/rec/
│   ├── rec_gt_train.txt    # Training labels
│   ├── rec_gt_val.txt      # Validation labels
│   └── thai_data/
│       ├── train/          # Training images
│       └── val/            # Validation images
```

### 3.3 การเช็คข้อมูล Dataset

```powershell
# ตรวจสอบรายชื่อ datasets ที่มี
Get-ChildItem -Directory thai-letters\datasets\converted\train_data_thai_paddleocr_*

# ตรวจสอบจำนวนไฟล์ในแต่ละ dataset
Get-ChildItem thai-letters\datasets\converted\train_data_thai_paddleocr_*\train_data\rec\thai_data\train | Measure-Object | Select-Object Count

# ตรวจสอบรายละเอียดของ dataset
Get-Content thai-letters\datasets\converted\train_data_thai_paddleocr_*\dataset_info.json -Head 20

# ตรวจสอบลักษณะข้อมูลตัวอย่าง
Get-Content thai-letters\datasets\converted\train_data_thai_paddleocr_*\train_data\rec\rec_gt_train.txt -Head 10
```

### 3.4 การเลือก Dataset ตาม Scenario

1. **Numbers Dataset (0-9 เท่านั้น)**
   - 🏆 **Best**: `train_data_thai_paddleocr_0807_1200`
   - ✅ 304 ไฟล์ (243 train, 61 val)
   - ✅ ได้ผลจริงแล้ว (13.3% accuracy)
   - ✅ เทรนเร็ว (13 นาที)
   - 🏅 **Architecture**: CRNN + MobileNetV3
   - 💰 **ค่าใช้จ่าย**: $0.11 (ml.g4dn.xlarge)
   - 🎯 **Use Case**: PoC, การทดสอบ infrastructure, การรู้จำตัวเลข

2. **Full Thai Text Dataset**
   - 🏆 **Best**: `train_data_thai_paddleocr_0804_1144`
   - ✅ 9,408 ไฟล์ (7,526 train, 1,882 val)
   - ✅ ครอบคลุมตัวอักษรไทยเต็มรูปแบบ
   - ✅ เหมาะสำหรับโมเดล production
   - 🏅 **Architecture**: SVTR_LCNet
   - 💰 **ค่าใช้จ่าย**: $25+ (ml.p3.2xlarge)
   - 🎯 **Use Case**: OCR เต็มรูปแบบ, เอกสารที่มีความซับซ้อน

3. **Mixed Dataset (ตัวเลขและตัวอักษรไทย)**
   - 🏆 **Best**: `train_data_thai_paddleocr_0805_1532`
   - ✅ 5,240 ไฟล์ (4,192 train, 1,048 val)
   - ✅ เหมาะสำหรับการใช้งานทั่วไป
   - ✅ สมดุลระหว่างความเร็วและความแม่นยำ
   - 🏅 **Architecture**: SVTR_LCNet หรือ CRNN+MobileNetV3
   - 💰 **ค่าใช้จ่าย**: $10-15 (ml.g4dn.xlarge)
   - 🎯 **Use Case**: การใช้งานทั่วไป, บัตรประชาชน, เอกสารทั่วไป

4. **Enhanced Thai Text Dataset**
   - 🏆 **Best**: `train_data_thai_paddleocr_0810_1630`
   - ✅ 12,560 ไฟล์ (10,048 train, 2,512 val)
   - ✅ มีเอฟเฟกต์หลากหลาย (การหมุน, ความสว่าง, การบิดเบี้ยว)
   - ✅ เหมาะสำหรับการใช้งานในสภาพแวดล้อมที่ท้าทาย
   - 🏅 **Architecture**: SVTR, NRTR, SRN
   - 💰 **ค่าใช้จ่าย**: $30+ (ml.p3.2xlarge)
   - 🎯 **Use Case**: การรู้จำในสภาพแสงไม่ดี, ภาพถ่ายจากมือถือ, เอกสารที่ไม่ชัดเจน

5. **Basic Thai Characters Dataset**
   - 🏆 **Best**: `train_data_thai_paddleocr_0812_0945`
   - ✅ 6,320 ไฟล์ (5,056 train, 1,264 val)
   - ✅ เน้นตัวอักษรไทยพื้นฐานที่ใช้บ่อย
   - ✅ เหมาะสำหรับการเริ่มต้นที่ต้องการความแม่นยำสูง
   - 🏅 **Architecture**: SVTR_LCNet, SRN
   - 💰 **ค่าใช้จ่าย**: $20+ (ml.g5.xlarge)
   - 🎯 **Use Case**: การรู้จำข้อความสั้นๆ, ป้ายต่างๆ, ชื่อสถานที่

### 3.5 วิธีการสร้าง Dataset ใหม่

การสร้าง dataset ใหม่สามารถทำได้โดยใช้สคริปต์ `thai_dataset_quick.py`:

```powershell
# ไปยังโฟลเดอร์ thai-letters
cd thai-letters

# สร้าง dataset ใหม่ด้วยการระบุจำนวนภาพต่อตัวอักษร
python thai_dataset_quick.py 20
# → เลือก dictionary ที่ต้องการ (number_dict.txt หรือ th_dict.txt)
# → เลือกเอฟเฟกต์ (0=ไม่มี, 9=ทั้งหมด, หรือเลือกเฉพาะ เช่น 1,2,3)

# สร้าง dataset แบบระบุพารามิเตอร์โดยตรง
python thai_dataset_quick.py 30 --dict=th_dict.txt --effects=1,2,3,5 --output=my_custom_dataset
```

### 3.6 การแปลง Dataset เป็นรูปแบบ PaddleOCR

```powershell
# แปลง dataset ที่สร้างไว้ให้อยู่ในรูปแบบที่ PaddleOCR ใช้ได้
python phase1_paddleocr_converter.py --input-path thai_dataset_YYYYMMDD_HHMM --output-path train_data_thai_paddleocr_YYYYMMDD_HHMM

# ตรวจสอบผลลัพธ์
dir train_data_thai_paddleocr_*\train_data\rec\

# ตรวจสอบจำนวนไฟล์ในชุดข้อมูล
Get-ChildItem train_data_thai_paddleocr_*\train_data\rec\thai_data\train | Measure-Object | Select-Object Count
```

### 3.7 ข้อควรระวังในการเลือก Dataset

1. **ขนาดของ Dataset**:
   - Dataset ที่ใหญ่เกินไปจะใช้เวลาเทรนนาน
   - Dataset ที่เล็กเกินไปอาจทำให้โมเดลไม่สามารถเรียนรู้ได้ดีพอ

2. **ความสมดุลของข้อมูล**:
   - ควรมีตัวอย่างของแต่ละตัวอักษรในจำนวนที่ใกล้เคียงกัน
   - หากมีตัวอักษรบางตัวมากเกินไป อาจทำให้โมเดลมี bias

3. **ความหลากหลายของข้อมูล**:
   - ควรมีตัวอย่างที่หลากหลาย (แบบอักษร, ขนาด, สี, พื้นหลัง)
   - ใช้เอฟเฟกต์เพื่อเพิ่มความหลากหลาย (rotation, brightness, contrast)

---

## 4. การเทรนแบบ Manual ทีละขั้นตอน

### 4.1 เตรียม Configuration Files

#### CRNN + MobileNetV3 (Fast & Efficient)
```powershell
# สร้าง config file สำหรับ CRNN
cp configs/rec/template/crnn_template.yml configs/rec/my_crnn_config.yml

# แก้ไข config ตามต้องการ
notepad configs/rec/my_crnn_config.yml
```

#### SVTR_LCNet (High Accuracy)
```powershell
# สร้าง config file สำหรับ SVTR_LCNet
cp configs/rec/template/svtr_template.yml configs/rec/my_svtr_config.yml

# แก้ไข config ตามต้องการ
notepad configs/rec/my_svtr_config.yml
```

### 4.2 ตรวจสอบ AWS Credentials
```powershell
# ตั้งค่า AWS credentials
$Env:AWS_ACCESS_KEY_ID="your_access_key"
$Env:AWS_SECRET_ACCESS_KEY="your_secret_key"
$Env:AWS_SESSION_TOKEN="your_session_token"

# ตรวจสอบว่าทำงานได้
aws sts get-caller-identity
```

### 4.3 อัปโหลด Dataset ไปยัง S3
```powershell
# เลือก dataset (ตัวอย่าง)
$DATASET_PATH="thai-letters/datasets/converted/train_data_thai_paddleocr_0807_1200"

# อัปโหลดไป S3
aws s3 sync $DATASET_PATH s3://paddleocr-dev-data-bucket/data/training/rec/ --exclude="*.log"

# ตรวจสอบว่าอัปโหลดสำเร็จ
aws s3 ls s3://paddleocr-dev-data-bucket/data/training/rec/ --human-readable
```

### 4.4 เตรียม Training Configuration

#### ตัวอย่าง: Config สำหรับ CRNN + MobileNetV3
```yaml
Global:
  use_gpu: true
  epoch_num: 50
  log_smooth_window: 20
  print_batch_step: 10
  save_model_dir: /opt/ml/model/
  save_epoch_step: 5
  character_dict_path: /opt/ml/input/data/training/th_dict.txt
  character_type: thai
  max_text_length: 25
  use_space_char: false
  distributed: false

Architecture:
  model_type: rec
  algorithm: CRNN
  Backbone:
    name: MobileNetV3
    scale: 0.5
    model_name: large
  Neck:
    name: SequenceEncoder
    encoder_type: rnn
    hidden_size: 96
  Head:
    name: CTCHead
    fc_decay: 0.00001

Loss:
  name: CTCLoss

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: 0.005
    warmup_epoch: 5
```

#### ตัวอย่าง: Config สำหรับ SVTR_LCNet
```yaml
Global:
  use_gpu: true
  epoch_num: 100
  log_smooth_window: 20
  print_batch_step: 10
  save_model_dir: /opt/ml/model/
  save_epoch_step: 10
  character_dict_path: /opt/ml/input/data/training/th_dict.txt
  character_type: thai
  max_text_length: 25
  use_space_char: true
  distributed: false

Architecture:
  model_type: rec
  algorithm: SVTR_LCNet
  Backbone:
    name: SVTRNet
    img_size: [64, 256]
    out_char_num: 25
    out_channels: 192

Loss:
  name: CTCLoss

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr:
    name: Cosine
    learning_rate: 0.001
    warmup_epoch: 5
```

### 4.5 รัน Training Job

#### การรัน Training Manual บน AWS SageMaker
```powershell
# ชื่อ job และวันที่
$JOB_NAME="thai-ocr-training-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$JOB_ALGORITHM="CRNN"  # หรือ "SVTR_LCNet"
$INSTANCE_TYPE="ml.g4dn.xlarge"  # เลือก instance ที่ต้องการ

# สร้าง training job
aws sagemaker create-training-job `
  --training-job-name $JOB_NAME `
  --algorithm-specification AlgorithmName=paddleocr-training `
  --role-arn "arn:aws:iam::484468818942:role/paddleocr-dev-sagemaker-role" `
  --input-data-config "ChannelName=training,DataSource={S3DataSource={S3Uri=s3://paddleocr-dev-data-bucket/data/training/}}" `
  --output-data-config "S3OutputPath=s3://paddleocr-dev-data-bucket/models/" `
  --resource-config "InstanceType=$INSTANCE_TYPE,InstanceCount=1,VolumeSizeInGB=30" `
  --hyper-parameters "epochs=50,learning_rate=0.005,batch_size=32,algorithm=$JOB_ALGORITHM"
```

#### การติดตามสถานะ
```powershell
# ตรวจสอบสถานะของ training job
aws sagemaker describe-training-job `
  --training-job-name $JOB_NAME `
  --query "TrainingJobStatus"

# ดู logs แบบ real-time
aws logs get-log-events `
  --log-group-name "/aws/sagemaker/TrainingJobs" `
  --log-stream-name $JOB_NAME/algo-1-XXXX
```

### 4.6 ดาวน์โหลดโมเดลที่เทรนแล้ว
```powershell
# ดาวน์โหลดโมเดลจาก S3
aws s3 cp s3://paddleocr-dev-data-bucket/models/$JOB_NAME/output/model.tar.gz ./models/

# แตกไฟล์
mkdir -p ./models/$JOB_NAME
tar -xvzf ./models/model.tar.gz -C ./models/$JOB_NAME
```

### 4.7 ทดสอบโมเดลที่เทรนแล้ว
```powershell
# ทดสอบโมเดล CRNN
python test_numbers_model.py --model-path ./models/$JOB_NAME

# หรือทดสอบโมเดล SVTR_LCNet
python test_sagemaker_model.py --model-path ./models/$JOB_NAME
```

---

## 5. การเตรียม AWS สำหรับการเทรนครั้งใหม่

### 5.1 หยุด Training Jobs ที่กำลังทำงาน
```powershell
# ดู training jobs ที่กำลังทำงาน
aws sagemaker list-training-jobs --status-equals InProgress

# หยุด training job ที่ไม่ต้องการ
aws sagemaker stop-training-job --training-job-name "thai-ocr-training-YYYYMMDD-HHMMSS"
```

### 5.2 ลบ Model Artifacts ที่ไม่ต้องการจาก S3
```powershell
# ดูรายการ model artifacts
aws s3 ls s3://paddleocr-dev-data-bucket/models/

# ลบ model artifacts ที่ไม่ต้องการ
aws s3 rm s3://paddleocr-dev-data-bucket/models/old-model-name/ --recursive

# ตรวจสอบหลังลบ
aws s3 ls s3://paddleocr-dev-data-bucket/models/
```

### 5.3 ล้าง CloudWatch Logs
```powershell
# ดูรายการ log streams
aws logs describe-log-streams --log-group-name "/aws/sagemaker/TrainingJobs"

# ลบ log stream ที่ไม่ต้องการ
aws logs delete-log-stream --log-group-name "/aws/sagemaker/TrainingJobs" --log-stream-name "thai-ocr-training-old-date"
```

### 5.4 อัพเดท Docker Image (ถ้าจำเป็น)
```powershell
# สร้าง Docker image ใหม่
docker build -f Dockerfile.sagemaker -t thai-ocr:latest .

# Tag และ push ไปยัง ECR
aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin 484468818942.dkr.ecr.ap-southeast-1.amazonaws.com
docker tag thai-ocr:latest 484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:latest
docker push 484468818942.dkr.ecr.ap-southeast-1.amazonaws.com/paddleocr-dev:latest
```

---

## 6. การปรับแต่ง Configuration ระดับสูง

### 6.1 พารามิเตอร์ที่ควรปรับแต่ง

#### Global Parameters - พารามิเตอร์ทั่วไป
```yaml
Global:
  use_gpu: true                    # เปิด/ปิดการใช้ GPU
  epoch_num: 100                   # จำนวนรอบการเทรน
  log_smooth_window: 20            # หน้าต่างการทำ smooth ของ log
  print_batch_step: 10             # จำนวน step ในการพิมพ์ log
  save_model_dir: ./output/        # ไดเร็กทอรีสำหรับบันทึกโมเดล
  save_epoch_step: 10              # บันทึกโมเดลทุกๆ กี่ epoch
  eval_batch_step: [0, 2000]       # batch step ในการประเมินผล [เริ่ม, ทุกๆ]
  cal_metric_during_train: true    # คำนวณ metrics ระหว่างการเทรน
  character_dict_path: ppocr/utils/dict/th_dict.txt  # path ไป dictionary
  character_type: th               # ภาษา (thai)
  max_text_length: 25              # ความยาวข้อความสูงสุด
  infer_mode: false                # โหมด inference
  use_space_char: true/false       # ใช้ space character
```

#### Architecture - สถาปัตยกรรมโมเดล
```yaml
Architecture:
  model_type: rec                  # recognition หรือ detection
  algorithm: SVTR_LCNet            # อัลกอริธึมหลัก (CRNN, SVTR_LCNet)
  Backbone:
    name: MobileNetV3              # backbone network
    scale: 0.5                     # scale factor
    model_name: large              # small หรือ large
  Neck:
    name: SequenceEncoder          # encoder ที่ใช้
    encoder_type: rnn              # rnn, reshape, fc
    hidden_size: 96                # hidden size
  Head:
    name: CTCHead                  # head ที่ใช้
    fc_decay: 0.00001              # L2 regularization
```

#### Optimizer - ตัวปรับค่าพารามิเตอร์
```yaml
Optimizer:
  name: Adam                       # Adam, SGD, Momentum
  beta1: 0.9                       # beta1 สำหรับ Adam
  beta2: 0.999                     # beta2 สำหรับ Adam
  lr:                              # learning rate scheduler
    name: Cosine                   # Cosine, Piecewise
    learning_rate: 0.001           # base learning rate
    warmup_epoch: 5                # epochs สำหรับ warmup
```

### 6.2 ผลกระทบของการเปลี่ยนแปลงพารามิเตอร์

| พารามิเตอร์ | เพิ่มค่า ⬆️ | ลดค่า ⬇️ |
|------------|------------|----------|
| **epoch_num** | ✅ accuracy สูงขึ้น<br>❌ ใช้เวลานานขึ้น | ✅ เร็วขึ้น<br>❌ อาจ underfit |
| **learning_rate** | ✅ เทรนเร็วขึ้น<br>❌ อาจไม่เสถียร | ✅ เสถียรขึ้น<br>❌ เทรนช้าลง |
| **batch_size** | ✅ เทรนเร็วขึ้น<br>✅ gradient เสถียรขึ้น<br>❌ ใช้ memory มากขึ้น | ✅ ใช้ memory น้อยลง<br>❌ gradient ไม่เสถียร |
| **hidden_size** | ✅ accuracy สูงขึ้น<br>❌ ใช้ memory มากขึ้น | ✅ ใช้ memory น้อยลง<br>❌ accuracy ลดลง |
| **backbone scale** | ✅ accuracy สูงขึ้น<br>❌ inference ช้าลง | ✅ inference เร็วขึ้น<br>❌ accuracy ลดลง |

### 6.3 ตัวอย่างการปรับแต่งตาม Use Case

#### โมเดลที่เน้นความแม่นยำสูง (Accuracy First)
```yaml
Architecture:
  algorithm: SVTR_LCNet
  Backbone:
    name: SVTRNet
    img_size: [64, 256]
    
Optimizer:
  name: Adam
  lr:
    name: Cosine
    learning_rate: 0.0005
    warmup_epoch: 10
```

#### โมเดลที่เน้นความเร็ว (Speed First)
```yaml
Architecture:
  algorithm: CRNN
  Backbone:
    name: MobileNetV3
    scale: 0.5
    model_name: small
  
Optimizer:
  name: SGD
  lr:
    name: Piecewise
    learning_rate: 0.01
```

#### โมเดลสำหรับตัวอักษรไทยโดยเฉพาะ (Thai-Optimized)
```yaml
Architecture:
  algorithm: SVTR_LCNet
  Backbone:
    name: SVTRNet
    img_size: [64, 320]  # ปรับความกว้างให้เหมาะกับภาษาไทย
    
Train:
  dataset:
    transforms:
      - RecResizeImg:
          image_shape: [3, 48, 320]  # เพิ่มความสูงสำหรับสระบน/ล่าง
```

---

## 7. แนวทางการแก้ไขปัญหาที่พบบ่อย

### 7.1 ปัญหาด้าน AWS
- **AWS Credentials หมดอายุ**: รัน `aws sts get-caller-identity` เพื่อตรวจสอบ
- **S3 Access Denied**: ตรวจสอบ IAM role และ bucket policy
- **ECR Authentication Error**: รัน `aws ecr get-login-password` เพื่อรับ token ใหม่

### 7.2 ปัญหาด้าน Training
- **Out of Memory**: ลด batch size หรือปรับ model size
- **Low Accuracy**: เพิ่ม epoch หรือปรับ learning rate
- **Slow Training**: ใช้ GPU instance ที่เร็วกว่า หรือลด dataset size
- **Model Not Found**: ตรวจสอบ S3 paths และการดาวน์โหลดโมเดล

### 7.3 ปัญหาด้าน Docker
- **Build Error**: รัน `docker system prune -f` และ build ใหม่
- **Push Error**: ตรวจสอบ ECR permissions และ image tags
- **Container Error**: ตรวจสอบ logs ใน CloudWatch

---

## 9. ตัวอย่างคำสั่งเทรนและดาวน์โหลดโมเดล

### 9.1 ตัวอย่างการเทรนแบบสมบูรณ์ (End-to-End)

#### ตัวอย่าง: เทรน CRNN + MobileNetV3 บน ml.g4dn.xlarge

```powershell
# 1. ตั้งค่า AWS Credentials
$Env:AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
$Env:AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
$Env:AWS_SESSION_TOKEN="YOUR_SESSION_TOKEN"
$Env:AWS_DEFAULT_REGION="ap-southeast-1"

# 2. อัปโหลด Dataset ไป S3
$DATASET_PATH="thai-letters/datasets/converted/train_data_thai_paddleocr_0807_1200"
aws s3 sync $DATASET_PATH s3://paddleocr-dev-data-bucket/data/training/rec/ --exclude="*.log"

# 3. ตรวจสอบ Dictionary
aws s3 cp thai-letters/th_dict.txt s3://paddleocr-dev-data-bucket/data/training/th_dict.txt

# 4. สร้าง Training Job สำหรับ CRNN
$TIMESTAMP = Get-Date -Format "yyyyMMdd-HHmmss"
$JOB_NAME = "thai-ocr-crnn-$TIMESTAMP"

aws sagemaker create-training-job `
  --training-job-name $JOB_NAME `
  --algorithm-specification AlgorithmName=paddleocr-training `
  --role-arn "arn:aws:iam::484468818942:role/paddleocr-dev-sagemaker-role" `
  --input-data-config "ChannelName=training,DataSource={S3DataSource={S3Uri=s3://paddleocr-dev-data-bucket/data/training/}}" `
  --output-data-config "S3OutputPath=s3://paddleocr-dev-data-bucket/models/" `
  --resource-config "InstanceType=ml.g4dn.xlarge,InstanceCount=1,VolumeSizeInGB=30" `
  --hyper-parameters "epochs=50,learning_rate=0.005,batch_size=32,algorithm=CRNN"

# 5. ติดตามสถานะ
aws sagemaker describe-training-job --training-job-name $JOB_NAME --query "TrainingJobStatus"

# 6. ดาวน์โหลดโมเดลหลังเทรนเสร็จ
mkdir -p ./models/$JOB_NAME
aws s3 cp s3://paddleocr-dev-data-bucket/models/$JOB_NAME/output/model.tar.gz ./models/$JOB_NAME/
tar -xvzf ./models/$JOB_NAME/model.tar.gz -C ./models/$JOB_NAME/

# 7. ทดสอบโมเดล
python test_numbers_model.py --model-path ./models/$JOB_NAME
```

#### ตัวอย่าง: เทรน SVTR_LCNet บน ml.p3.2xlarge

```powershell
# 1. อัปโหลด Dataset ขนาดใหญ่ไป S3
$DATASET_PATH="thai-letters/datasets/converted/train_data_thai_paddleocr_0804_1144"
aws s3 sync $DATASET_PATH s3://paddleocr-dev-data-bucket/data/training/rec/ --exclude="*.log"

# 2. สร้าง Training Job สำหรับ SVTR_LCNet
$TIMESTAMP = Get-Date -Format "yyyyMMdd-HHmmss"
$JOB_NAME = "thai-ocr-svtr-$TIMESTAMP"

aws sagemaker create-training-job `
  --training-job-name $JOB_NAME `
  --algorithm-specification AlgorithmName=paddleocr-training `
  --role-arn "arn:aws:iam::484468818942:role/paddleocr-dev-sagemaker-role" `
  --input-data-config "ChannelName=training,DataSource={S3DataSource={S3Uri=s3://paddleocr-dev-data-bucket/data/training/}}" `
  --output-data-config "S3OutputPath=s3://paddleocr-dev-data-bucket/models/" `
  --resource-config "InstanceType=ml.p3.2xlarge,InstanceCount=1,VolumeSizeInGB=30" `
  --hyper-parameters "epochs=100,learning_rate=0.001,batch_size=64,algorithm=SVTR_LCNet"

# 3. ดูสถานะพร้อม log แบบ real-time (สามารถใช้ Ctrl+C เพื่อออกได้)
aws logs tail /aws/sagemaker/TrainingJobs --log-stream-name $JOB_NAME/algo-1 --follow
```

### 9.2 ตัวอย่างการดาวน์โหลดและเตรียมโมเดล

```powershell
# 1. ดาวน์โหลดโมเดลทั้งหมดจาก S3
$JOB_NAME = "thai-ocr-crnn-20250811-123456"  # แทนด้วยชื่อ job ของคุณ
mkdir -p ./models/$JOB_NAME

# 2. ดาวน์โหลด model.tar.gz
aws s3 cp s3://paddleocr-dev-data-bucket/models/$JOB_NAME/output/model.tar.gz ./models/$JOB_NAME/

# 3. แตกไฟล์
tar -xvzf ./models/$JOB_NAME/model.tar.gz -C ./models/$JOB_NAME/

# 4. ตรวจสอบไฟล์โมเดล
ls -la ./models/$JOB_NAME/

# 5. คัดลอกไฟล์สำคัญไปยังโฟลเดอร์ inference
mkdir -p ./models/inference
cp ./models/$JOB_NAME/best_accuracy.pdparams ./models/inference/
cp ./models/$JOB_NAME/config.yml ./models/inference/
```

### 9.3 ตัวอย่างการเทรนแบบ One-line Command (สำหรับการทดสอบเร็วๆ)

```powershell
# เทรน CRNN ด้วยคำสั่งเดียว
aws sagemaker create-training-job --training-job-name "thai-ocr-quick-test-$(Get-Date -Format 'yyyyMMdd-HHmmss')" --algorithm-specification AlgorithmName=paddleocr-training --role-arn "arn:aws:iam::484468818942:role/paddleocr-dev-sagemaker-role" --input-data-config "ChannelName=training,DataSource={S3DataSource={S3Uri=s3://paddleocr-dev-data-bucket/data/training/}}" --output-data-config "S3OutputPath=s3://paddleocr-dev-data-bucket/models/" --resource-config "InstanceType=ml.g4dn.xlarge,InstanceCount=1,VolumeSizeInGB=30" --hyper-parameters "epochs=10,learning_rate=0.005,batch_size=32,algorithm=CRNN"
```

## 10. การวัดผลและประเมินโมเดล

### 10.1 วิธีการวัดผลโมเดล OCR

#### วัดผลด้วย Character Accuracy
```powershell
# ทดสอบกับชุด validation แบบมาตรฐาน
python test_sagemaker_model.py --model-path ./models/$JOB_NAME --metrics

# หรือใช้เฉพาะสำหรับ Numbers
python test_numbers_model.py --model-path ./models/$JOB_NAME --metrics
```

ผลลัพธ์ที่ได้:
```
Character Accuracy: 13.3% (2/15 ตัวอักษรถูกต้อง)
Word Accuracy: 13.3% (2/15 คำถูกต้อง)
Average Confidence: 0.0974
Execution Time: 0.532 seconds per image
```

#### วัดผลด้วย Confusion Matrix
```powershell
# สร้าง confusion matrix
python test_sagemaker_model.py --model-path ./models/$JOB_NAME --confusion-matrix
```

#### การวัดผลด้วย Real-world Data
```powershell
# ทดสอบกับข้อมูลจริงจากภายนอก
python test_sagemaker_model.py --model-path ./models/$JOB_NAME --test-dir ./external_test_images --output-json ./test_results.json
```

### 10.2 การเปรียบเทียบโมเดลต่างๆ

| Metric | CRNN + MobileNetV3 | SVTR_LCNet |
|--------|------------------|-----------|
| Character Accuracy | 13.3% | 72.5% |
| Inference Speed | 12ms/image | 35ms/image |
| Model Size | 9.2MB | 23.5MB |
| Training Time | 13 นาที | 25+ ชั่วโมง |
| Training Cost | $0.11 | $25 |
| สำหรับ | ตัวเลข, PoC | Thai text, Production |

### 10.3 การประเมินคุณภาพโมเดล

#### ประเมินด้วย Expected Metrics
- **Character Accuracy ที่ยอมรับได้**: >50% สำหรับตัวเลข, >70% สำหรับตัวอักษรไทย
- **Inference Speed ที่ต้องการ**: <50ms/image บน CPU, <15ms/image บน GPU
- **ความหลากหลายของรูปแบบตัวอักษร**: ทดสอบกับฟอนต์อย่างน้อย 5 แบบ
- **ความทนทานต่อสภาพแวดล้อม**: ทดสอบกับภาพที่มีแสง, มุมมอง, และการรบกวนต่างๆ

#### Quality Assurance Checklist
- [ ] ทดสอบกับตัวอักษรทุกตัวในภาษาไทย
- [ ] ทดสอบกับตัวเลขทั้ง 0-9
- [ ] ทดสอบกับขนาดภาพต่างๆ
- [ ] ทดสอบกับความละเอียดต่างๆ
- [ ] ทดสอบกับพื้นหลังต่างๆ

### 10.4 แนวทางการปรับปรุง Accuracy

1. **Data Quality**: เพิ่มคุณภาพและความหลากหลายของข้อมูล
   ```powershell
   # สร้างข้อมูลที่มีคุณภาพสูงและหลากหลาย
   cd thai-letters
   python thai_dataset_quick.py 500 --quality=high --effects=all
   ```

2. **Hyperparameter Optimization**: ปรับแต่ง hyperparameters
   ```yaml
   # ตัวอย่าง: ปรับ learning rate และ batch size
   Optimizer:
     name: Adam
     lr:
       name: Cosine
       learning_rate: 0.0008  # ปรับลงเล็กน้อย
       warmup_epoch: 8       # เพิ่ม warmup
   ```

3. **Model Ensembling**: ใช้หลายโมเดลร่วมกัน
   ```python
   # ตัวอย่างโค้ด Python สำหรับ model ensembling
   predictions_model1 = model1.predict(image)
   predictions_model2 = model2.predict(image)
   
   # เลือกผลลัพธ์ที่มี confidence สูงกว่า
   final_prediction = predictions_model1 if predictions_model1["confidence"] > predictions_model2["confidence"] else predictions_model2
   ```

4. **Post-processing**: ใช้ context และ dictionary
   ```python
   # ตัวอย่างการใช้ dictionary เพื่อแก้ไขคำที่ใกล้เคียง
   def correct_with_dictionary(prediction, thai_dictionary):
       # หาคำที่ใกล้เคียงที่สุดใน dictionary
       closest_word = find_closest_word(prediction, thai_dictionary)
       return closest_word
   ```
