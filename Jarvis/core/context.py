from typing import Dict, Any
from Jarvis.core.memory.execution_memory import ExecutionMemory


class TempMemory(ExecutionMemory):
    """
    Memória temporária separada que herda contrato de ExecutionMemory.
    Pode ser expandida para TTL, limites, debug etc.
    """
    pass


class ExecutionContext:
    """
    Estado compartilhado de runtime do Jarvis.
    Guarda flags e memórias que o Executor / Pipeline usam.
    """

    def __init__(self):
        # Flags simples de runtime
        self.dev_mode: bool = False
        self.offline: bool = False
        self.llm_available: bool = True

        # Memórias baseadas na implementação oficial
        self.execution_memory: ExecutionMemory = ExecutionMemory()
        self.temp_memory: TempMemory = TempMemory()

        # Extras (logs, dados transientes)
        self.extra: Dict[str, Any] = {}

    def __repr__(self) -> str:
        return (
            f"<ExecutionContext dev_mode={self.dev_mode} offline={self.offline} "
            f"llm_available={self.llm_available}>"
        )

    def enable_dev(self) -> None:
        self.dev_mode = True

    def disable_dev(self) -> None:
        self.dev_mode = False

    def set_offline(self, value: bool) -> None:
        self.offline = bool(value)
