from dataclasses import dataclass
from typing import Any, Dict, Optional
from Jarvis.core.intent import IntentType


@dataclass
class ActionRequest:
    intent: IntentType
    params: Dict[str, Any]
    context: Any
    action: Optional[str] = None   
    risk: str = "low"                   
    metadata: Dict[str, Any] | None = None  