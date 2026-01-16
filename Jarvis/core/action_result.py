from dataclasses import dataclass
from typing import Any, Literal


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
    success: bool
    message: str
    data: Any | None = None

    source: SourceType = "local"
    confidence: float | None = None
