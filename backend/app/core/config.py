import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DYNAMIC_MODEL_PATH = str(BASE_DIR / "model" / "model_v3.h5")


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    MODEL_PATH: str = DYNAMIC_MODEL_PATH
    LLM_MODEL: str = "models/gemini-2.5-flash"


settings = Settings()
