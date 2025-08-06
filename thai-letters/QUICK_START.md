# Quick Reference - Thai Dataset Generator

## 🚀 Quick Start

```bash
# Generate interactive dataset
python thai_dataset_quick.py 10
```

Follow the prompts:
1. **Select Dictionary**: `number_dict.txt` (11 chars) or `th_dict.txt` (881 chars)
2. **Choose Effects**: `0` (none), `9` (all), or custom like `1,2,3`

## 📁 Key Files

- **`thai_dataset_quick.py`**: Main interactive generator (ENHANCED ✨)
- **`thai_dataset_generator.py`**: Core generation engine
- **`README.md`**: Full documentation
- **`CHANGELOG.md`**: Version history and improvements

## 🎛️ Effects Available

| # | Effect | Description |
|---|--------|-------------|
| 1 | Rotation | -2 to +2 degrees |
| 2 | Brightness | 0.8-1.2 range |
| 3 | Contrast | 0.8-1.2 range |
| 4 | Blur | 0-0.4 range |
| 5 | Noise | 0-0.05 range |
| 6 | Position | left/center/right |
| 7 | Padding | 15-25 pixels |
| 8 | Compression | 85-100% quality |

## 📐 Image Specs

- **Size**: 128 x 96 pixels (+50% height)
- **Fonts**: 42-84 pixels range
- **Format**: JPEG, RGB
- **Optimized**: For Thai characters with tone marks

## 📝 Examples

```bash
# Clean test images
python thai_dataset_quick.py 1
# → number_dict.txt → 0 (no effects)

# Training dataset  
python thai_dataset_quick.py 20
# → th_dict.txt → 9 (all effects)

# Custom effects
python thai_dataset_quick.py 15
# → th_dict.txt → 1,2,6 (rotation+brightness+position)
```

**Output**: `datasets/raw/thai_dataset_[size]_[samples]samples_[dict]_[effects]_[timestamp]/`
