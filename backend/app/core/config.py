import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- THE DYNAMIC PATH MAGIC ---
# 1. Path(__file__).resolve() gets the exact location of this config.py file
# 2. .parent.parent.parent goes up 3 folders: core -> app -> backend
# 3. We then attach the models folder and the file name to that root path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DYNAMIC_MODEL_PATH = str(BASE_DIR / "model" / "my_model.h5")


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    # Use our dynamically generated path
    MODEL_PATH: str = DYNAMIC_MODEL_PATH
    # Updated to the latest Gemini Pro model
    LLM_MODEL: str = "models/gemini-2.5-pro"


settings = Settings()
