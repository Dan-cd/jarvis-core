from Jarvis.core.decision import DecisionOutcome, DecisionPath
from Jarvis.core.dev_mode_guard import DevModeGuard
from Jarvis.core.context import ExecutionContext


class Executor:
    def __init__(self, llm, fallback, sandbox, memory, context: ExecutionContext, answer_pipeline, DevModeGuard):
        self.llm = llm
        self.fallback = fallback
        self.sandbox = sandbox
        self.memory = memory
        self.context = context
        self.answer_pipeline = answer_pipeline
        self.dev_guard = DevModeGuard

    def execute(self, decision, user_input: str) -> str:

        if decision.outcome == DecisionOutcome.REQUIRE_DEV_MODE:
            if self.dev_guard.is_blocked():
                return "Dev Mode temporariamente bloqueado."

            attempt = input("Senha do Dev Mode: ")

            if self.dev_guard.validate(attempt):
                self.context.dev_mode = True
                return "Modo desenvolvedor ativado."
            else:
                return "Senha incorreta."
            
        if self.context.dev_mode and user_input.lower() in ("sair do modo dev", "exit dev", "dev off"):
            self.context.dev_mode = False
            return "Modo desenvolvedor desativado."


        if decision.outcome != DecisionOutcome.ALLOW:
            return decision.reason or "Operação interrompida."

        if decision.path == DecisionPath.SANDBOX:
            return self.sandbox.handle(decision, self.memory)

        if decision.path == DecisionPath.LLM:
            return self.answer_pipeline.respond(
                user_input=user_input,
                context=self.context   
            )

        if decision.path == DecisionPath.FALLBACK:
            return self.fallback.respond(user_input)

        return "Caminho não reconhecido."