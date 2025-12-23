
from Jarvis.core.config import Config
from Jarvis.core.errors import ErrorManager
from Jarvis.core.router import Router
from Jarvis.core.context import ExecutionContext

class Jarvis:
    def __init__(self, router, config: Config | None = None):
        self.config = config or Config()
        self.error_manager = ErrorManager(self.config)
        self.router = router
        self.context = router.context
        print("[Jarvis] Inicializando...")

    def start(self):
        print("[Jarvis] Sistema iniciado.")
        self.main_loop()

    def main_loop(self):
        print("[Jarvis] Aguardando comandos... (digite 'exit' para encerrar)")

        while True:
            prefix = "[DEV] " if self.context.dev_mode else ""
            user_input = input(f"{prefix}> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "sair"):
                print("[Jarvis] Encerrando sistema...")
                break

            result = self.router.route(user_input)
            print(result)