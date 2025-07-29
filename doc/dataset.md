# Dataset Generation & Conversion

This guide describes how to generate synthetic Thai OCR data, annotate real data, and convert datasets to PaddleOCR format.

## Data Generation

### 1. Synthetic Data Generation

Scripts:
- `thai-letters/quick_phase1_generator.py`  – Quick synthetic data generation
- `thai-letters/quick_thai_generator.py`    – Alternate generator
- `thai-letters/thai_dataset_generator.py`  – Comprehensive generator

Usage:
```bash
python thai-letters/quick_phase1_generator.py --output synthetic_data/ --count 1000 --fonts path/to/fonts
```

### 2. Real Data Annotation

Use your annotated dataset:
- `thai-letters/thai_dataset_comprehensive_30samples_0722_1551/`
- `thai-letters/thai_dataset_minimal_5samples_0724_1154/`

Format:
```
image/{id}.jpg \t x1,y1,x2,y2,x3,y3,x4,y4,text
```

## Conversion to PaddleOCR Format

### Scripts
- `thai-letters/phase1_paddleocr_converter.py`
- `thai-letters/quick_phase1_converter.py`

Usage:
```bash
python thai-letters/phase1_paddleocr_converter.py --input-path thai_dataset_comprehensive_30samples_0722_1551/ --output-path train_data_thai_paddleocr_0724_1157/
```

Structure:
```
train_data_thai_paddleocr_0724_1157/
├── image/
├── label/
├── train_list.txt
└── val_list.txt
```
