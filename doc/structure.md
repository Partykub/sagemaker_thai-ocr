# Project Structure & File Organization

This document outlines the recommended directory layout and file placement for the Thai OCR project to ensure modularity, maintainability, and clarity.

## Root Directory

```
/ (project root)
├── doc/                           # Project documentation
├── configs/                       # PaddleOCR YAML config files
├── scripts/                       # Custom training and inference scripts
├── thai-letters/                  # Data generation and annotation tools
├── train_data_thai_paddleocr_*/   # Converted PaddleOCR datasets
├── th_dict.txt                    # Thai character dictionary
├── development-task.md                # Development task list
└── README.md                      # Project overview and quick start
```

### Directories

- **doc/**: Contains Markdown documentation for every major component (overview, installation, dataset, training, deployment, Terraform).  
- **configs/**: Stores model configuration files (`*.yml`) for detection and recognition. Keep separate for local and SageMaker training.  
- **scripts/**: Place custom Python scripts for training orchestration (e.g., SageMaker entrypoints, inference utilities).  
- **thai-letters/**: Data generation scripts, converters, and example datasets.  
- **train_data_thai_paddleocr_***/: Output of annotation conversion to PaddleOCR format, ready for training.  

### Files

- **th_dict.txt**: Comprehensive Thai character dictionary for recognition.  
- **development-task.md**: Ongoing list of development tasks aligned with documentation and project milestones.  
- **README.md**: High-level project description, quick start instructions, and links to detailed docs.  

## Best Practices

1. **Modularity**: Keep data prep, training, and inference logic in separate folders or modules.  
2. **Naming Conventions**: Use clear, descriptive names for scripts and configs (e.g., `train_thai_recognition.py`, `thai_svtr_tiny_config.yml`).  
3. **Version Control**: Track changes in `configs/` and `scripts/` actively; avoid committing large datasets (use `.gitignore`).  
4. **Documentation**: Update `doc/structure.md` whenever adding new directories or moving files.  
5. **Reusability**: Scripts in `scripts/` should accept CLI arguments for paths and hyperparameters to support both local and cloud usage.  
