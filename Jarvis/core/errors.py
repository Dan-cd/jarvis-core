from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Optional
import traceback


class JarvisError(Exception):
    """
    Base exception para o Jarvis.
    Todas as exceções específicas devem herdar desta.
    """

    def __init__(
        self,
        message: str,
        origin: str,
        module: Optional[str] = None,
        function: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Args:
            message: Mensagem legível para logs/usuário (quando necessário).
            origin: Parte do sistema que originou o erro (ex: "llm", "executor").
            module: Nome do módulo Python onde ocorreu.
            function: Nome da função/método onde ocorreu.
            original_exception: Exceção original (para traceback).
        """
        self.message = message
        self.origin = origin
        self.module = module
        self.function = function
        self.original_exception = original_exception
        self.timestamp = datetime.now()
        super().__init__(message)

    def __str__(self):
        return f"[{self.origin}] {self.message}"



# Exceções semânticas usadas no fluxo


class WebRequiredButUnavailable(JarvisError):
    """Lançado quando a consulta exige web, mas nenhum WebPlugin disponível."""
    pass


class InvalidAnswerOrigin(JarvisError):
    """Lançado quando Executor recebe origem inválida."""
    pass


class ExecutorContractViolation(JarvisError):
    """Violação de contrato entre Router / Executor / Plugins."""
    pass


class PluginError(JarvisError):
    """Erro originado em um plugin específico."""
    pass


class InvalidActionResult(JarvisError):
    """
    Ação retornou um resultado que não satisfaz o contrato esperado
    (ex.: ActionResult inválido).
    """
    pass


class LLMUnavailable(JarvisError):
    """
    Lançado quando não há nenhum LLM disponível no LLMManager.
    """
    pass


class LLMExecutionError(JarvisError):
    """
    Erro ao executar um LLM (fallback acabou, ou provider levantou erro).
    """
    pass



# Gerenciamento de erros (ErrorManager)


class ErrorManager:
    """
    Responsável por logar erros e notificar de acordo com tipo/origem.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.log_path = Path(self.config.get("error_log_path", "data/logs/error.log"))

    def handle(self, error: JarvisError) -> None:
        """
        Entrada unificada para lidar com erros.
        Registra no log e notifica conforme tipo/origem.
        """

        try:
            self._log_error(error)

            if isinstance(error, PluginError) or error.origin == "plugin":
                self._handle_plugin_error(error)
            elif isinstance(error, ExecutorContractViolation) or error.origin == "core":
                self._handle_core_error(error)
            else:
                self._handle_generic_error(error)

        except Exception as fatal_error:
            self._emergency_log(error, fatal_error)

    def _handle_plugin_error(self, error: JarvisError) -> None:
        # Notifica usuário e possivelmente desativa plugin
        print(f"[JARVIS][PLUGIN_ERROR] {error.message}")

    def _handle_core_error(self, error: JarvisError) -> None:
        # Notifica falha crítica de core
        print(f"[JARVIS][CORE_ERROR] {error.message}")

    def _handle_generic_error(self, error: JarvisError) -> None:
        # Notifica erro padrão
        print(f"[JARVIS][ERROR] {error.message}")

    def _log_error(self, error: JarvisError) -> None:
        """
        Loga o erro no arquivo configurado.
        """

        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(f"[{error.timestamp.isoformat()}] {error.origin.upper()} | "
                    f"{error.module or 'unknown'}.{error.function or 'unknown'} | "
                    f"{error.message}\n")

            if error.original_exception:
                f.write("Original exception:\n")
                f.write("".join(traceback.format_exception(
                    type(error.original_exception),
                    error.original_exception,
                    error.original_exception.__traceback__,
                )))
                f.write("\n")

    def _emergency_log(self, original_error: JarvisError, fatal_error: Exception) -> None:
        """
        Se o logging falhar, registra de forma simples para não perder o erro.
        """
        try:
            em_path = Path(self.config.get("emergency_log_path", "data/logs/emergency.log"))
            em_path.parent.mkdir(parents=True, exist_ok=True)

            with em_path.open("a", encoding="utf-8") as f:
                f.write(f"EMERGENCY at {datetime.now().isoformat()}\n")
                f.write(f"Original: {original_error.message}\n")
                f.write(f"Handler failure: {repr(fatal_error)}\n\n")
        except Exception:
            pass  # Se nem o emergency log funcionar, nada a fazer
