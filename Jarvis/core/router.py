from Jarvis.core.intent import IntentEngine
from Jarvis.core.policy import PolicyEngine, PolicyResult
from Jarvis.core.types import IntentType
from Jarvis.core.answer_pipeline import AnswerPipeline

class Router:
    def __init__(self, context, llm_manager, answer_pipeline, sandbox, memory):
        self.context = context
        self.intent_engine = IntentEngine()
        self.policy_engine = PolicyEngine(context)
        self.llm = llm_manager
        self.answer_pipeline = answer_pipeline
        self.sandbox = sandbox
        self.memory = memory

    def route(self, user_input: str) -> str:
        intent = self.intent_engine.parse(user_input)

        #  Intenção não reconhecida -> explicação
        if not self.context.llm_available:
            return "No momento estou operando sem conexão, mas continuo disponível para comandos."

        if not intent:
            return self.answer_pipeline.explain(
                "Não consegui compreender, pode repetir porfavor?"
            )
        
    
        #  Avaliação de política
        decision = self.policy_engine.evaluate(intent)

        if decision.result == PolicyResult.REQUIRE_DEV_MODE:
            if not self.context.dev_mode:
                return self.answer_pipeline.explain(
                    decision.reason or
                    "Essa ação requer permissões avançadas."
                )

        if decision.result == PolicyResult.DENY:
            return self.answer_pipeline.explain(
                decision.reason or
                "Essa ação não é permitida."
            )

        #  Intenções explicativas (help)
        if intent.name == "help":
            return self.answer_pipeline.explain(
                self.context.describe_system()
            )

        #  Intenções de sandbox (dev)
        if intent.name.startswith("dev."):
            return self.sandbox.handle(intent, self.context)
        

        if not intent:
            return "Não consegui compreender, pode repetir por favor?"

        if intent.name == "system.help":
            base = (
                "Posso interpretar comandos simples, responder perguntas básicas "
                "e registrar ações executadas quando solicitado."
            )
            return self.answer_pipeline.explain(base)

        if intent.name == "memory.query":
            actions = self.memory.get_recent_actions()

            if not actions:
                return "Ainda não executei nenhuma ação."

            base = "Aqui está um resumo das últimas ações que executei:\n"
            for act in actions:
                base += f"- {act}\n"

            return self.answer_pipeline.explain(base)

        return "Não consegui compreender, pode repetir por favor?"       
    

    def handle_memory_query(self):
        memories = self.memory.recall()

        if not memories:
            raw = "Eu ainda não tenho conversas anteriores salvas na memória."
        else:
            last = memories[-1]["content"]
            raw = f"Eu lembro que, na última conversa, você disse: {last}"

        return self.llm.reformulate(raw)