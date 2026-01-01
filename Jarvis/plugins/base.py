from abc import ABC, abstractmethod
from Jarvis.core.action_request import ActionRequest
from Jarvis.core.action_result import ActionResult


class Plugin(ABC):
    metadata = {}

    @abstractmethod
    def execute(self, action: ActionRequest) -> ActionResult:
        pass
