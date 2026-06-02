# Text-to-SQL Training Pipeline

This folder contains notebooks and scripts for Spider dataset conversion, QLoRA fine-tuning config, and adapters publishing.

## Components

- `configs/`: YAML configurations for PEFT parameters and Hugging Face target adapters.
- `notebooks/`: Colab-ready Jupyter notebook (`finetune_sqlcoder_spider_qlora.ipynb`).
- `scripts/`:
  - `convert_spider_to_sqlcoder.py`: Preprocessing dataset script.
  - `train_qlora.py`: PEFT fine-tuning loop script.
  - `push_adapter.py`: Weight upload script to HF Hub.
