from abc import ABC, abstractmethod
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult

class Plugin(ABC):
    metadata = {
        "name": "",
        "risk_level": "low",
        "destructive": False,
        "supports_dry_run": True,
        "requires_confirmation": False
    }

    @abstractmethod
    def execute(self, action: ActionRequest, dry_run: bool = False) -> ActionResult:
        pass