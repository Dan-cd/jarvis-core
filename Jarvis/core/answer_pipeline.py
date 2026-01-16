from Jarvis.core.llm_contract import LLMRequest, LLMVerbosity
from Jarvis.core.context import ExecutionContext
from Jarvis.plugins_available.web.models import WebResult


class AnswerPipeline:
    def __init__(self, llm, execution_memory):
        self.llm = llm
        self.execution_memory = execution_memory

    def respond(self, user_input: str, context: ExecutionContext) -> str:
        return self._respond_internal(user_input, context, None)

    def respond_with_web(self, user_input: str, web_data: WebResult, context: ExecutionContext) -> str:
        return self._respond_internal(user_input, context, web_data)

    def _respond_internal(self, user_input, context, web_result):
        source = self.execution_memory.get("last_source", "local")
        confidence = self.execution_memory.get("last_confidence")

        verbosity = LLMVerbosity.SHORT if context.dev_mode else LLMVerbosity.NORMAL
        max_tokens = 400 if context.dev_mode else 1800

        system_rules = (
            "Você é o Jarvis.\n"
            "Você é um sistema executor.\n"
            "Nunca diga que foi treinado com dados.\n"
            "Nunca afirme acesso genérico à internet.\n"
            "Nunca diga que não sabe a origem da informação.\n"
            "Sempre explique a origem com base no sistema Jarvis.\n"
        )

        if source == "web":
            system_rules += "Esta resposta veio de uma busca web.\n"
        elif source == "memory":
            system_rules += "Esta resposta veio da memória do usuário.\n"
        elif source == "plugin":
            system_rules += "Esta resposta foi produzida por um plugin local.\n"
        elif source == "llm":
            system_rules += "Esta resposta foi gerada por raciocínio interno.\n"

        request = LLMRequest(
            prompt=user_input,
            system_rules=system_rules,
            verbosity=verbosity,
            max_tokens=max_tokens,
            context_data={"web": web_result.__dict__ if web_result else None}
        )

        response = self.llm.generate(request)
        return response.text.strip()
