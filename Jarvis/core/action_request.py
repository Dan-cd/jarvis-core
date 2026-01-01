from dataclasses import dataclass
from typing import Any, Dict
from Jarvis.core.intent import IntentType


@dataclass
class ActionRequest:
    intent: IntentType
    params: Dict[str, Any]
    context: Any