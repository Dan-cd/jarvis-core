from dataclasses import dataclass
from pathlib import Path

@dataclass
class ActionPlan:
    action: str
    targets: list[Path]
    destructive: bool
    description: str