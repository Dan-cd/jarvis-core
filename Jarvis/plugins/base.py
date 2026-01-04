from abc import ABC, abstractmethod
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult


class Plugin(ABC):
    metadata = {
        "name": "filesystem",
        "destructive": True,
        "supports_dry_run": True,
        "requires_confirmation": True
    }

    @abstractmethod
    def execute(self, action: ActionRequest) -> ActionResult:
        pass
