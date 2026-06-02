import os
import argparse
import yaml
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

def train(config_path: str, dataset_path: str, output_adapter_dir: str):
    print(f"Loading configuration from {config_path}...")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    model_cfg = config["model_config"]
    lora_cfg = config["lora_config"]
    train_args_cfg = config["training_arguments"]
    dataset_cfg = config["dataset"]
    
    # Override dataset path if provided via CLI
    train_file = dataset_path if dataset_path else dataset_cfg["train_file"]
    
    print(f"Base model ID: {model_cfg['base_model_id']}")
    print(f"Dataset path: {train_file}")
    
    # 1. Quantization Configuration (4-bit NF4)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    # 2. Load Tokenizer
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_cfg["base_model_id"],
        trust_remote_code=True
    )
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    # 3. Load Quantized Base Model
    print("Loading 4-bit quantized base model...")
    base_model = AutoModelForCausalLM.from_pretrained(
        model_cfg["base_model_id"],
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        trust_remote_code=True
    )
    
    # 4. Prepare model for k-bit training
    base_model = prepare_model_for_kbit_training(base_model)
    
    # 5. PEFT/LoRA Setup
    print("Configuring LoRA adapter parameters...")
    peft_config = LoraConfig(
        r=lora_cfg["r"],
        lora_alpha=lora_cfg["lora_alpha"],
        lora_dropout=lora_cfg["lora_dropout"],
        target_modules=lora_cfg["target_modules"],
        bias=lora_cfg["bias"],
        task_type=lora_cfg["task_type"]
    )
    
    model = get_peft_model(base_model, peft_config)
    model.print_trainable_parameters()
    
    # 6. Load Converted Dataset
    print("Loading converted JSONL dataset...")
    dataset = load_dataset("json", data_files={"train": train_file})
    
    # 7. Configure Training Arguments
    # Merge custom CLI destination into config dictionary
    train_args_cfg["output_dir"] = train_args_cfg.get("output_dir", "./checkpoints")
    
    training_args = TrainingArguments(
        output_dir=train_args_cfg["output_dir"],
        num_train_epochs=train_args_cfg["num_train_epochs"],
        per_device_train_batch_size=train_args_cfg["per_device_train_batch_size"],
        gradient_accumulation_steps=train_args_cfg["gradient_accumulation_steps"],
        learning_rate=train_args_cfg["learning_rate"],
        optim=train_args_cfg["optim"],
        warmup_ratio=train_args_cfg["warmup_ratio"],
        lr_scheduler_type=train_args_cfg["lr_scheduler_type"],
        logging_steps=train_args_cfg["logging_steps"],
        save_strategy=train_args_cfg["save_strategy"],
        evaluation_strategy=train_args_cfg["evaluation_strategy"],
        fp16=train_args_cfg["fp16"],
        bf16=train_args_cfg["bf16"],
        max_grad_norm=train_args_cfg["max_grad_norm"],
        weight_decay=train_args_cfg["weight_decay"],
        remove_unused_columns=False
    )
    
    # 8. SFTTrainer
    print("Initializing SFTTrainer...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        peft_config=peft_config,
        dataset_text_field="text",
        max_seq_length=dataset_cfg["max_seq_length"],
        tokenizer=tokenizer,
        args=training_args,
    )
    
    # Disabling cache during training to support gradient checkpointing
    model.config.use_cache = False
    
    # 9. Train!
    print("Starting QLoRA training loop...")
    trainer.train()
    
    # 10. Save Adapter Weight Checkpoint
    print(f"Saving fine-tuned adapter weights to {output_adapter_dir}...")
    trainer.model.save_pretrained(output_adapter_dir)
    print("Training process finished successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QLoRA fine-tune SQLCoder on Spider dataset.")
    parser.add_argument("--config", type=str, required=True, help="Path to config yaml file")
    parser.add_argument("--dataset", type=str, required=True, help="Path to converted training JSONL dataset")
    parser.add_argument("--output_adapter", type=str, required=True, help="Directory to save the trained adapter weights")
    
    args = parser.parse_args()
    train(args.config, args.dataset, args.output_adapter)
