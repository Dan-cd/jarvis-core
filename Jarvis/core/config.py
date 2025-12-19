from pathlib import Path

class Config:
    DEV_PASSWORD = "@64wg702"
    
    def __init__(self):
        self.use_audio = False
        self.use_llm = False
        self.debug = True
        base_dir = Path(__file__).resolve().parents[2]

        self.BASE_DIR = base_dir
        self.SANDBOX_DIR = base_dir / "Jarvis" / "sandbox"