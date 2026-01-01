from enum import Enum
from dataclasses import dataclass
from Jarvis.core.action_request import ActionRequest


class PolicyResult(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_DEV_MODE = "require_dev_mode"


@dataclass
class PolicyDecision:
    result: PolicyResult
    reason: str | None = None


class PolicyEngine:
    def __init__(self, context):
        self.context = context

    def evaluate_intent(self, intent):
        if intent.name in ("dev.enter", "dev.exit"):
            return PolicyDecision(PolicyResult.ALLOW)

        if intent.name.startswith("dev."):
            return PolicyDecision(
                PolicyResult.REQUIRE_DEV_MODE,
                "Comando exclusivo do modo desenvolvedor."
            )

        return PolicyDecision(PolicyResult.ALLOW)

    def evaluate_action(self, action: ActionRequest, dev_mode: bool) -> PolicyDecision:
        if action.risk == "high" and not dev_mode:
            return PolicyDecision(
                PolicyResult.REQUIRE_DEV_MODE,
                "Ação sensível requer modo desenvolvedor."
            )

        if action.action.startswith("filesystem.delete") and not dev_mode:
            return PolicyDecision(
                PolicyResult.REQUIRE_DEV_MODE,
                "Exclusão de arquivos requer modo desenvolvedor."
            )

        return PolicyDecision(PolicyResult.ALLOW)

