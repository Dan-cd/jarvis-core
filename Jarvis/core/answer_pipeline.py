from Jarvis.core.llm_contract import (
    LLMRequest,
    LLMVerbosity,
)
from Jarvis.core.context import ExecutionContext


class AnswerPipeline:
    """
    Controla completamente:
    - O tom
    - A verbosidade
    - O que o LLM pode ou não afirmar
    """

    def __init__(self, llm):
        self.llm = llm

    def respond(self, user_input: str, context: ExecutionContext) -> str:
        """
        Usado SOMENTE quando a resposta vem do LLM.
        Plugins e executor não passam por aqui.
        """

        
        #  MODO DE RESPOSTA
        

        if context.dev_mode:
            verbosity = LLMVerbosity.SHORT
            max_tokens = 500
        else:
            verbosity = LLMVerbosity.NORMAL
            max_tokens = 3000

       
        #  REGRAS DURAS
       

        system_rules = (
            "Você é o Jarvis.\n"
            "Fale como um mordomo neutro, direto e educado.\n"
            "Nunca afirme que executou ações reais.\n"
            "Nunca diga que criou, editou ou apagou arquivos.\n"
            "Nunca finja acesso ao sistema do usuário.\n"
            "Nunca mencione arquitetura interna, APIs ou custos.\n"
        )

        if context.dev_mode:
            system_rules += (
                "Modo desenvolvedor ativo:\n"
                "- Seja extremamente direto.\n"
                "- Sem rodeios ou explicações longas.\n"
                "- Pode comentar decisões internas do sistema.\n"
            )

        
        #  REQUEST AO LLM
        

        request = LLMRequest(
            prompt=user_input,
            system_rules=system_rules,
            verbosity=verbosity,
            max_tokens=max_tokens,
        )

        response = self.llm.generate(request)

        return self._hard_cut(response.text, context)

   
    #  CORTE DURO
    

    def _hard_cut(self, text: str, context: ExecutionContext) -> str:
        max_chars = 250 if context.dev_mode else 800
        return text[:max_chars].strip()