import os
import logging
from app.core.config import settings

logger = logging.getLogger("text-to-sql-backend")

# Global variables to cache model and tokenizer
_model = None
_tokenizer = None

def get_model_and_tokenizer():
    """
    Returns cached model and tokenizer. Loads them if not already cached.
    In mock mode, returns (None, None).
    """
    global _model, _tokenizer
    
    if settings.MOCK_MODEL:
        logger.info("Running in MOCK mode. Model and tokenizer will not be loaded.")
        return None, None
        
    if _model is not None and _tokenizer is not None:
        return _model, _tokenizer
        
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
        from peft import PeftModel
    except ImportError:
        logger.error(
            "Model loading libraries (torch, transformers, peft) are not installed. "
            "Install optional dependencies using 'pip install -e .[ml]'"
        )
        raise RuntimeError("ML dependencies are missing, cannot load model.")

    logger.info(f"Loading tokenizer for {settings.BASE_MODEL_ID}...")
    _tokenizer = AutoTokenizer.from_pretrained(
        settings.BASE_MODEL_ID,
        token=settings.HF_TOKEN
    )
    
    logger.info(f"Loading base model {settings.BASE_MODEL_ID} on device {settings.DEVICE}...")
    
    # 4-bit configuration if device is cuda and double quantization is supported
    bnb_config = None
    if settings.DEVICE == "cuda":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        
    base_model = AutoModelForCausalLM.from_pretrained(
        settings.BASE_MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto" if settings.DEVICE == "cuda" else None,
        torch_dtype=torch.float16 if settings.DEVICE == "cuda" else torch.float32,
        token=settings.HF_TOKEN
    )
    
    # Load LoRA adapter if available
    if settings.HF_ADAPTER_REPO:
        logger.info(f"Loading LoRA adapter from {settings.HF_ADAPTER_REPO}...")
        _model = PeftModel.from_pretrained(
            base_model,
            settings.HF_ADAPTER_REPO,
            token=settings.HF_TOKEN
        )
    else:
        logger.info("No HF_ADAPTER_REPO specified. Using base model for inference.")
        _model = base_model
        
    if settings.DEVICE != "cuda" and hasattr(_model, "to"):
        _model = _model.to(settings.DEVICE)
        
    _model.eval()
    logger.info("Model and tokenizer loaded successfully!")
    return _model, _tokenizer
