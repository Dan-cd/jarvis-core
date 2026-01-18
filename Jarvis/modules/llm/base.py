from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMRequest:
    prompt: str
    mode: str = "default"
    system: Optional[str] = None
    temperature: float = 0.7


@dataclass
class LLMResponse:
    text: str


class LLMInterface(ABC):
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        pass
