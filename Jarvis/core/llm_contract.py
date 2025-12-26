from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


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


@dataclass
class LLMResponse:
    text: str
    confidence: float | None = None
    raw: dict | None = None


class LLMInterface(ABC):
    """
    CONTRATO DEFINITIVO DO LLM
    O LLM:
    - recebe um pedido estruturado
    - retorna apenas texto bruto
    - não decide estado, ações ou modo
    """

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        pass