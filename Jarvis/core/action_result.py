from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ActionResult:
    success: bool
    message: str
    data: Dict[str, Any] | None = None