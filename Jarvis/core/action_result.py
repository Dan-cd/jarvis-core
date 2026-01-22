from dataclasses import dataclass
from typing import Any, Literal, Optional


SourceType = Literal[
    "llm",
    "web",
    "plugin",
    "local",
    "fallback",
    "memory",
]


@dataclass
class ActionResult:
    # Mantemos compatibilidade com chamadas posicionais (success, message, ...)
    success: bool = True
    message: str = ""
    data: Any | None = None

    # Conteúdo textual principal retornado pelo executor/plugin
    content: Optional[str] = None

    # Origem da resposta (sinônimo de 'source')
    origin: SourceType = "local"
    source: SourceType = "local"

    # Confiança da resposta (0.0 - 1.0)
    confidence: float | None = None
