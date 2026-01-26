from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class DecisionOutcome(Enum):
    ALLOW = auto()
    DENY = auto()
    REQUIRE_DEV_MODE = auto()
    OFFLINE = auto()


class DecisionPath(Enum):
    LLM = auto()
    FALLBACK = auto()
    SANDBOX = auto()
    LOCAL = auto()
    PLUGIN = auto()


@dataclass
class Decision:
    def __init__(
        self,
        path,
        payload,
        requires_web=False,
        reason=None,
        outcome=None
    ):
        self.path = path
        self.payload = payload
        self.requires_web = requires_web
        self.reason = reason
        self.outcome = outcome

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
