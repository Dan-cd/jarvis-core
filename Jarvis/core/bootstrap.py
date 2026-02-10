from dotenv import load_dotenv
import os
from pathlib import Path


def bootstrap_env():
    base_dir = Path.cwd()
    dotenv_path = base_dir / ".env"
    load_dotenv(dotenv_path=str(dotenv_path))

    if not os.getenv("GROQ_API_KEY"):
        print("⚠️ GROQ_API_KEY não encontrada. Sistema iniciará em modo offline/local se possível.")