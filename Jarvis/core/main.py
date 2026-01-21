from typing import Optional

from Jarvis.core.config import Config
from Jarvis.core.errors import JarvisError, ErrorManager
from Jarvis.core.router import Router
from Jarvis.core.executor import Executor
from Jarvis.core.answer_pipeline import AnswerPipeline
from Jarvis.core.LLMManager import LLMManager


class Jarvis:
    """
    Aplicação principal do Jarvis (CLI).
    
    - Recebe dependências (Router, Executor, Context, Output Formatter).
    - Estabelece o loop principal.
    - Usa ErrorManager para capturar erros institucionais.
    """

    def __init__(
        self,
        router: Router,
        executor: Executor,
        answer_pipeline: AnswerPipeline,
        llm_manager: Optional[LLMManager] = None,
        config: Optional[Config] = None,
    ):
        self.config = config or Config()
        self.error_manager = ErrorManager(self.config)

        self.router = router
        self.context = router.context  # Única fonte válida de contexto

        self.executor = executor
        self.answer_pipeline = answer_pipeline
        self.llm_manager = llm_manager

        print("[Jarvis] Inicializando sistema...")

        # Mostra apenas info relevante
        if hasattr(self.config, "GROQ_MODEL"):
            print(f"[Jarvis] Groq model configurado: {self.config.GROQ_MODEL}")

    def start(self):
        print("[Jarvis] Sistema iniciado.")
        self.main_loop()

    def main_loop(self):
        print("[Jarvis] Aguardando comandos... (digite 'exit' para encerrar)")

        while True:
            try:
                prefix = "[DEV] " if self.context.dev_mode else ""
                user_input = input(f"{prefix}> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ("exit", "quit", "sair"):
                    print("[Jarvis] Encerrando sistema...")
                    break

                decision = self.router.route(user_input)
                raw_response = self.executor.execute(decision, user_input)

                # raw_response já foi formatado pelo AnswerPipeline internalemente
                print(raw_response)

            except JarvisError as je:
                # Captura erros institucionais e usa o ErrorManager
                self.error_manager.handle(je)
            except Exception as unexpected:
                # Qualquer erro inesperado também é reportado
                self.error_manager.handle(
                    JarvisError(
                        message=str(unexpected),
                        origin="core.main",
                        module="Jarvis",
                        function="main_loop",
                        original_exception=unexpected,
                    )
                )

        print("[Jarvis] Sistema finalizado.")
