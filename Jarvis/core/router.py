from Jarvis.core.intent import IntentEngine
from Jarvis.core.policy import PolicyEngine, PolicyResult
from Jarvis.core.context import ExecutionContext


class Router:
    def __init__(self, context: ExecutionContext):
        self.context = context
        self.intent_engine = IntentEngine()
        self.policy_engine = PolicyEngine(context)

    def route(self, user_input: str) -> str:
        intent = self.intent_engine.parse(user_input)

        if not intent:
            return "Comando não reconhecido."

        decision = self.policy_engine.evaluate(intent)

        # Dev mode required
        if decision.result == PolicyResult.REQUIRE_DEV_MODE:
            if not self.context.dev_mode:
                return decision.reason or "Ação não permitida fora do dev mode."
            if decision.result == PolicyResult.ALLOW:
                if intent.name.startswith("dev."):
                    return self.sandbox.execute(intent)

                return "Ação permitida. (execução futura)"

        # Execução controlada
        if intent.name == "dev.enter":
            self.context.dev_mode = True
            return "Dev mode ativado."

        if intent.name == "dev.exit":
            self.context.dev_mode = False
            return "Dev mode desativado."

        return "Ação permitida. (execução futura)"