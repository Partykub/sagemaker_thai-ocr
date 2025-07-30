# Recognition Model Configurations

This directory contains PaddleOCR configuration files for Thai text recognition models.

## Files:
- `thai_rec.yml` - Main Thai recognition config for local training
- `thai_rec_dev.yml` - Development config (reduced epochs for testing)
- `thai_rec_prod.yml` - Production config (optimized hyperparameters)

## Usage:
```bash
# Local training
python PaddleOCR/tools/train.py -c configs/rec/thai_rec.yml

# Development testing
python PaddleOCR/tools/train.py -c configs/rec/thai_rec_dev.yml
```
