import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Yojana.ai"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "yojana_ai_super_secret_jwt_key_2026_sc_beneficiary")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    OTP_EXPIRE_MINUTES: int = int(os.getenv("OTP_EXPIRE_MINUTES", "5"))
    OTP_COOLDOWN_SECONDS: int = int(os.getenv("OTP_COOLDOWN_SECONDS", "60"))
    OTP_MAX_ATTEMPTS: int = int(os.getenv("OTP_MAX_ATTEMPTS", "3"))
    OTP_DEV_MODE: bool = os.getenv("OTP_DEV_MODE", "True").lower() in ("true", "1", "t")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./yojana.db")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-3B-Instruct")

settings = Settings()
