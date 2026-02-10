from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from typing import Any


class LLMVerbosity(Enum):
    SILENT = "silent"
    SHORT = "short"
    NORMAL = "normal"
    DEBUG = "debug"


@dataclass
class LLMRequest:
    prompt: str
    system_rules: str
    verbosity: LLMVerbosity = LLMVerbosity.NORMAL
    max_tokens: int | None = None
    context_data: dict[str, Any] | None = None


@dataclass
class LLMResponse:
    text: str
    confidence: float | None = None
    raw: dict | None = None


class LLMInterface(ABC):
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        pass
