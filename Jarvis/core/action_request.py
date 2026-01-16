from dataclasses import dataclass
from typing import Any, Dict, Optional
from Jarvis.core.intent import Intent

@dataclass
class ActionRequest:
    intent: Intent
    params: Dict[str, Any]
    context: Any
    action: Optional[str] = None
    risk: str = "low"
    metadata: Dict[str, Any] | None = None