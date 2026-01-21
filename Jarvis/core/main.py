# Jarvis/core/main.py
from typing import Optional

from Jarvis.core.config import Config
from Jarvis.core.errors import JarvisError, ErrorManager
from Jarvis.core.router import Router
from Jarvis.core.executor import Executor
from Jarvis.core.answer_pipeline import AnswerPipeline
from Jarvis.core.LLMManager import LLMManager
from Jarvis.core.context import ExecutionContext, TempMemory
from Jarvis.core.memory.execution_memory import ExecutionMemory


class Jarvis:
    """
    Aplicação core do Jarvis (loop CLI).
    Essa versão espera receber componentes já inicializados e
    garante que context.execution_memory e context.temp_memory
    existam (contrato v6.5).
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

        # O contexto deve ser unificado no bootstrap e passado ao router/executor.
        # Aqui aceitamos que router.context já exista; se não, criamos um novo.
        self.context: ExecutionContext = getattr(router, "context", None) or ExecutionContext()

        # Assegura que as memórias existam (contrato)
        if not hasattr(self.context, "execution_memory") or self.context.execution_memory is None:
            self.context.execution_memory = ExecutionMemory()
        if not hasattr(self.context, "temp_memory") or self.context.temp_memory is None:
            self.context.temp_memory = TempMemory()

        self.executor = executor
        self.answer_pipeline = answer_pipeline
        self.llm_manager = llm_manager

        print("[Jarvis] Inicializando sistema...")
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

                # Executor/AnswerPipeline já retornam string final
                print(raw_response)

            except JarvisError as je:
                self.error_manager.handle(je)
            except Exception as unexpected:
                # Garanta que tudo vira JarvisError para tratamento institucional
                je = JarvisError(
                    message=str(unexpected),
                    origin="core.main",
                    module="Jarvis",
                    function="main_loop",
                    original_exception=unexpected,
                )
                self.error_manager.handle(je)

        print("[Jarvis] Sistema finalizado.")
