# Dataset Generation & Conversion

This guide describes how to generate synthetic Thai OCR data for PaddleOCR training.

## Current Dataset Status

✅ **Ready-to-Use Dataset**: `thai-letters/train_data_thai_phase1_0729_1331/`
- **Training samples**: 3,117 images with Thai text labels
- **Validation samples**: 753 images with Thai text labels  
- **Total**: 3,870 synthetic Thai OCR images
- **Format**: PaddleOCR standard format
- **Content**: Thai characters and syllables with various fonts and augmentations

## Data Generation

### 1. Synthetic Data Generation (Completed)

**Primary Script**: `thai-letters/quick_phase1_generator.py`
- Generates Thai characters and syllables with multiple fonts
- Applies random augmentations (obstacles, noise, distortions)
- Creates PaddleOCR-compatible dataset structure

**Generation Command**:
```bash
cd thai-letters
python quick_phase1_generator.py
```

**Output Structure**:
```
train_data_thai_phase1_0729_1331/
├── train_data/
│   └── rec/
│       ├── rec_gt_train.txt        # Training labels (3,117 samples)
│       ├── rec_gt_val.txt          # Validation labels (753 samples)
│       └── thai_data/
│           ├── train/              # Training images
│           └── val/                # Validation images
└── PHASE1_DATASET_REPORT.md        # Generation summary
```

### 2. Label Format

**PaddleOCR Standard Format**:
```
thai_data/train/000_00.jpg	บิ
thai_data/train/000_01.jpg	บิ
thai_data/train/001_00.jpg	ร่ำ
```

Each line: `relative_image_path[TAB]thai_text`

## Alternative Scripts (Legacy)

- `thai-letters/thai_dataset_generator.py`  – Comprehensive generator
- `thai-letters/quick_thai_generator.py`    – Alternate generator
- `thai-letters/phase1_paddleocr_converter.py` – Format converter

## Dataset Verification

To verify the current dataset:
```bash
cd thai-letters/train_data_thai_phase1_0729_1331/train_data/rec

# Count training samples
Get-Content rec_gt_train.txt | Measure-Object -Line

# Count validation samples  
Get-Content rec_gt_val.txt | Measure-Object -Line

# Check image files
Get-ChildItem thai_data/train/*.jpg | Measure-Object
Get-ChildItem thai_data/val/*.jpg | Measure-Object
```
