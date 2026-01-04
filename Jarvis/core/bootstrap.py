from dotenv import load_dotenv
import os
from pathlib import Path


def bootstrap_env():
    base_dir = Path(__file__).resolve().parents[2]
    dotenv_path = base_dir / ".env"
    load_dotenv(dotenv_path=str(dotenv_path))

    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError(
            "GROQ_API_KEY não encontrada. Verifique o .env e o diretório de execução."
        )