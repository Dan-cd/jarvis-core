import subprocess
import sys
from pathlib import Path
from typing import Dict
from Jarvis.dev import simulate

class SandboxExecutor:
    def __init__(self, context, sandbox_dir: Path):
        self.sandbox_dir = sandbox_dir.resolve()
        self.context = context
    def execute(self, intent):
        return simulate.handle(intent, self.context)

    def run(self, file_path: Path) -> Dict[str, str | bool | None]:
        file_path = file_path.resolve()

        # Segurança mínima: só roda coisas dentro do sandbox

        if not file_path.exists():
            return {
                "sucess": False,
                "output": "",
                "error": "Arquivo não existe."
            }
        
        if self.sandbox_dir not in file_path.parents:
            return {
                "sucess": False,
                "output": "",
                "error": "Execução fora do sandbox não é permitida."
            }
        
        try:
            result = subprocess.run(
                [sys.executable, str(file_path)],
                capture_output = True,
                text=True,
                timeout=5
            )

            return {
                "sucess": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.returncode != 0 else None
            }
        
        except subprocess.TimeoutExpired:
            return {
                "sucess": False,
                "output": "",
                "error": "Execução excedeu o tempo limite."
            }
        
        except Exception as e:
            return {
                "sucess": False,
                "output": "",
                "error": f"Erro inesperado: {e}"
            }
    