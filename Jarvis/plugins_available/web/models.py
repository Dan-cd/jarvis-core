from dataclasses import dataclass
from typing import List


@dataclass
class WebRequest:
    query: str


@dataclass
class WebResult:
    query: str
    content: str
    sources: List[str]
    confidence: float
    is_summary: bool = False
    is_partial: bool = False
