from dataclasses import dataclass


@dataclass
class WebRequest:
    query: str


@dataclass
class WebResult:
    query: str
    content: str
    source: str
    confidence: float
    is_summary: bool
    is_partial: bool
