# Jarvis/core/errors.py
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pathlib import Path
import traceback


class JarvisError(Exception):
    """
    Erro base usado em todo o sistema para encapsular metadados.
    """

    def __init__(
        self,
        message: str,
        origin: str,
        module: Optional[str] = None,
        function: Optional[str] = None,
        sensitive: bool = False,
        source: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        self.message = message
        self.source = source
        self.origin = origin
        self.module = module
        self.function = function
        self.sensitive = sensitive
        self.original_exception = original_exception
        self.timestamp = datetime.now()
        super().__init__(message)


# Exceções semânticas que o resto do código pode capturar
class WebRequiredButUnavailable(JarvisError):
    """Lançado quando uma consulta exige Web e o WebPlugin não está disponível."""
    pass


class InvalidAnswerOrigin(JarvisError):
    """Lançado quando o Executor recebe um caminho/origem inválido."""
    pass


class ExecutorContractViolation(JarvisError):
    """Violação de contrato entre Router/Executor/Plugins."""
    pass


class PluginError(JarvisError):
    """Erro originado em um plugin específico."""
    pass


class ErrorManager:
    """
    Gerencia logging e notificações de erros.
    Mantive a mesma ideia do seu arquivo original, mas com tratamento
    de tipos e funções mais claras.
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.log_path = Path(self.config.get("error_log_path", "data/logs/error.log"))

    def handle(self, error: JarvisError) -> None:
        """
        Entrada unificada para lidar com erros.
        O comportamento:
          - registra no log
          - dispara handlers por origem
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
            # Em caso de falha na gestão de erros, grava emergência sem lançar
            self._emergency_log(error, fatal_error)

    def _handle_plugin_error(self, error: JarvisError) -> None:
        # Placeholder: comportamento específico para plugins
        self._notify_user(f"Plugin sensível '{error.module}' desativado por segurança.")

    def _handle_core_error(self, error: JarvisError) -> None:
        # Placeholder: colapsa para modo degradado
        self._notify_user("Erro crítico no core. Sistema entrou no modo degradado.")

    def _handle_generic_error(self, error: JarvisError) -> None:
        self._notify_user(f"Erro ocorrido em {error.module or 'desconhecido'}: {error.message}")

    def _log_error(self, error: JarvisError) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(f"[{error.timestamp.isoformat()}] {error.origin.upper()} | "
                    f"{(error.module or 'unknown')}.{(error.function or 'unknown')} | "
                    f"{error.message}\n")
            if error.original_exception:
                f.write("Original exception:\n")
                f.write("".join(traceback.format_exception(
                    type(error.original_exception),
                    error.original_exception,
                    error.original_exception.__traceback__,
                )))
                f.write("\n")

    def _disable_plugin(self, module: Optional[str]) -> None:
        # Implementação de desativação de plugin ficaria aqui
        pass

    def _notify_user(self, message: str) -> None:
        # Em v6.5 apenas print; futuramente pode ser UI/Socket/Event
        print(f"[JARVIS] {message}")

    def _emergency_log(self, original_error: JarvisError, fatal_error: Exception) -> None:
        try:
            em_path = Path(self.config.get("emergency_log_path", "data/logs/emergency.log"))
            em_path.parent.mkdir(parents=True, exist_ok=True)
            with em_path.open("a", encoding="utf-8") as f:
                f.write(f"EMERGENCY while handling error at {datetime.now().isoformat()}\n")
                f.write(f"Original: {original_error.message}\n")
                f.write(f"Handler failure: {repr(fatal_error)}\n\n")
        except Exception:
            # nada a fazer se até o emergency log falhar
            pass
