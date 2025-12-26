
from Jarvis.core.llm_contract import (
    LLMRequest,
    LLMVerbosity,
)
from Jarvis.core.context import ExecutionContext


class AnswerPipeline:
    def __init__(self, llm):
        self.llm = llm

    def respond(self, user_input: str, context: ExecutionContext) -> str:
        """
        Controla COMPLETAMENTE o que o LLM pode dizer.
        """

       
        #  Definir modo de resposta
        

        if context.dev_mode:
            verbosity = LLMVerbosity.SHORT
            max_tokens = 120
        else:
            verbosity = LLMVerbosity.NORMAL
            max_tokens = 300

        
        #  Regras duras do sistema
        

        system_rules = (
            "Você é o Jarvis.\n"
            "Fale como um mordomo neutro, direto e educado.\n"
            "Nunca explique limitações internas.\n"
            "Nunca mencione APIs, custos ou arquitetura.\n"
        )

        if context.dev_mode:
            system_rules += (
                "Modo desenvolvedor ativo:\n"
                "- Seja extremamente direto.\n"
                "- Sem explicações longas.\n"
                "- Sem introduções desnecessárias.\n"
            )

        
        #  Criar request estruturado
        

        request = LLMRequest(
            prompt=user_input,
            system_rules=system_rules,
            verbosity=verbosity,
            max_tokens=max_tokens,
        )

        
        #  Chamar LLM
        

        response = self.llm.generate(request)

        
        #  Corte duro de segurança
        

        return self._hard_cut(response.text, context)

    
    # Corte duro (anti-fala demais)
    

    def _hard_cut(self, text: str, context: ExecutionContext) -> str:
        if context.dev_mode:
            max_chars = 250
        else:
            max_chars = 800

        return text[:max_chars].strip()