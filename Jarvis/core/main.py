
from Jarvis.core.config import Config
from Jarvis.core.errors import ErrorManager

class Jarvis:
    def __init__(self, router, executor, context, output_formatter, config: Config | None = None):
        self.config = config or Config()
        self.error_manager = ErrorManager(self.config)
        self.router = router
        self.context = router.context
        self.executor = executor
        self.output_formatter = output_formatter
        self.context = context

        print("[Jarvis] Inicializando...")
        try:
            print(f"[Jarvis] Groq model: {self.config.GROQ_MODEL}")
        except Exception:
            pass

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

            decision = self.router.route(user_input)
            raw_response = self.executor.execute(decision, user_input)
            final_output = self.output_formatter.format(raw_response)

            print(final_output)