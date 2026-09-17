import logging
import threading
from typing import Tuple, Optional, Any

logger = logging.getLogger(__name__)

class ModelLoader:
    _instance: Optional['ModelLoader'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'ModelLoader':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelLoader, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.tokenizer: Any = None
        self.model: Any = None
        self.device: str = "cpu"
        self.is_model_loaded: bool = False
        self.is_loading: bool = False
        self.load_error: Optional[str] = None

    def load_model(self, model_name: str = "Qwen/Qwen2.5-3B-Instruct") -> bool:
        """Load Hugging Face model and tokenizer into memory ONCE at application startup."""
        with self._lock:
            if self.is_model_loaded:
                logger.info("Model is already loaded in memory.")
                return True

            if self.is_loading:
                logger.info("Model loading is already in progress in another thread.")
                return False

            self.is_loading = True
            logger.info(f"Initializing local LLM model loading: {model_name}...")

            try:
                import torch
                import os

                # Hardware Auto-Detection
                if torch.cuda.is_available():
                    self.device = "cuda"
                    torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
                    logger.info(f"Hardware Detected: CUDA GPU ({torch.cuda.get_device_name(0)})")
                else:
                    self.device = "cpu"
                    torch_dtype = torch.float32
                    cpu_threads = min(8, os.cpu_count() or 4)
                    torch.set_num_threads(cpu_threads)
                    logger.info(f"Hardware Detected: CPU (Configured PyTorch with {cpu_threads} threads)")

                from transformers import AutoTokenizer, AutoModelForCausalLM

                # Load Tokenizer
                logger.info(f"Loading tokenizer for {model_name}...")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    trust_remote_code=True,
                    padding_side="left"
                )
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token

                # Load Causal LM Model
                logger.info(f"Loading causal LM model weights for {model_name} on {self.device}...")
                if self.device == "cuda":
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        torch_dtype=torch_dtype,
                        device_map="auto",
                        trust_remote_code=True
                    )
                else:
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        torch_dtype=torch_dtype,
                        trust_remote_code=True
                    ).to(self.device)

                self.model.eval()
                self.is_model_loaded = True
                self.load_error = None
                logger.info(f"Successfully loaded {model_name} onto device: {self.device}")
                return True

            except Exception as e:
                err_msg = f"Local LLM notice: {str(e)}"
                logger.warning(err_msg)
                logger.warning("System running with Rule-Based Engine & Compatibility Scoring.")
                self.is_model_loaded = False
                self.load_error = err_msg
                return False
            finally:
                self.is_loading = False

    def is_available(self) -> bool:
        return self.is_model_loaded and self.model is not None and self.tokenizer is not None and not self.is_loading

    def get_status(self) -> dict:
        return {
            "loaded": self.is_model_loaded,
            "loading": self.is_loading,
            "device": self.device,
            "error": self.load_error
        }

model_loader = ModelLoader()

