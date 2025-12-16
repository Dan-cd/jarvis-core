from datetime import datetime
from typing import Optional
from pathlib import Path
import traceback


class JarvisError(Exception):
    def __init__(
            self,
            message: str,
            origin: str,
            module: Optional[str] = None,
            function: Optional[str] = None,
            sensitive: bool = False,
            source: str | None = None,
            original_exception: Optional[Exception] = None
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

class ErrorManager:
    def __init__(self, config):
        self.config = config
        self.log_path = Path("data/logs/error.log")

    def handle(self, error):
        try:
            self._log_error(error)

            if error.origin == "plugin":
                self._handle_plugin_error(error)
            elif error.origin == "core":
                self._handle_core_error(error)
            else:
                self._handle_generic_error(error)

        except Exception as fatal_error:
            self._emergency_log(error, fatal_error)

    def _handle_plugin_error(self, error: JarvisError):
        self._notify_user(
            f"Plugin sensível '{error.module}' desativado por segurança."
        )

    def _handle_core_error(self, error):
        self._notify_user(
            f"Erro crítico no core. Sistema entrou no modo degradado"
        )

    def _handle_generic_error(self, error: JarvisError):
        self._notify_user(
            f"Erro ocorrido em {error.module or 'desconhecido'}."
        )

    def _log_error(self, error: JarvisError):
        self.log_path.parent.mkdir(parents=True, exists_ok=True)

        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(
                f"[{error.timestamp}] "
                f"{error.origin.upper()} | "
                f"{error.module}.{error.function} | "
                f"{error.message}\n"
            )

            if error.original_exception:
                f.write(
                    traceback.format_exception(
                        type(error.original_exception),
                        error.original_exception,
                        error.original_exception.__traceback__,
                    )
                )
                f.write("\n")

    def _disable_plugin(self, module: Optional[str]):
        pass

    def _notify_user(self, message: str):
        print(f"[JARVIS] {message}")

    def _emergency_log(self, original_error: JarvisError, fatal_error: Exception):
        try:
            with open("data/logs/emergency.log", "a", encoding="utf-8") as f:
                f.write(
                    f" EMERENCY FAILURE while handling error: \n"
                    f"{original_error.message}\n"
                    f"{fatal_error}\n\n"
                )
        except Exception:
            pass