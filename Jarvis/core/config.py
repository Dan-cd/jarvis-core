from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    DEV_MODE_PASSWORD = os.getenv("DEV_MODE_PASSWORD")
    
    def __init__(self):
        self.use_audio = False
        self.use_llm = False
        self.debug = True
        base_dir = Path(__file__).resolve().parents[2]

        self.BASE_DIR = base_dir
        self.SANDBOX_DIR = base_dir / "Jarvis" / "sandbox"
    
    @staticmethod
    def validate():
        if not Config.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY não definida no ambiente")