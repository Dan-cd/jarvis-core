from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class DecisionOutcome(Enum):
    ALLOW = auto()
    DENY = auto()
    REQUIRE_DEV_MODE = auto()
    OFFLINE =auto()

class DecisionPath(Enum):
    LLM = auto()
    FALLBACK = auto()
    SANDBOX = auto()
    LOCAL = auto()


@dataclass
class Decision:
    outcome: DecisionOutcome
    path: Optional[DecisionPath] = None
    reason: Optional[str] = None
    payload: Optional[dict] = None

    @classmethod
    def final(cls, outcome: DecisionOutcome, reason: str):
        return cls(outcome=outcome, reason=reason)
    
    @classmethod
    def route(cls, path: DecisionPath, payload: Optional[dict] = None):
        return cls(outcome=DecisionOutcome.ALLOW, path=path, payload=payload)