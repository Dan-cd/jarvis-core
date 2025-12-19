from enum import Enum
from dataclasses import dataclass

class PolicyResult(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_DEV_MODE = "require_dev_mode"

VALID_ACTIONS = {"DELETE"}
VALID_SCOPES = {"SYSTEM_CRITICAL", "USER_FILES"}

@dataclass
class PolicyDecision:
    result: PolicyResult
    reason: str | None = None


class PolicyEngine:
    def __init__(self, context):
        self.context = context

    def evaluate(self, intent) -> PolicyDecision:
        # comandos DEV
        if intent.name == "dev.enter" or intent.name == "dev.exit":
            return PolicyDecision(PolicyResult.ALLOW)
        if intent.name.startswith("dev."):
            return PolicyDecision(
                PolicyResult.REQUIRE_DEV_MODE,
                "Comando exclusivo do dev mode."
            )

        # ações sensíveis
        if intent.name == "force_delete":
            return PolicyDecision(
                PolicyResult.REQUIRE_DEV_MODE,
                "Ação sensível. Requer dev mode."
            )

        return PolicyDecision(PolicyResult.ALLOW)


