class ExecutionContext:
    def __init__(self, llm_available: bool = True):
        self.dev_mode: bool = False
        self.permissions: set[str] = set()
        self.llm_available: bool = llm_available

    def describe_system(self) -> str:
        """
        Retorna uma descrição crua das capacidades atuais do sistema.
        Essa resposta será posteriormente lapidada pelo AnswerPipeline.
        """
        features = [
            "Interpretar comandos de texto",
            "Responder perguntas gerais",
            "Executar comandos básicos com segurança",
            "Possuir um modo desenvolvedor com permissões avançadas",
            "Manter memória curta da conversa atual",
        ]

        description = (
            "Este é o sistema Jarvis.\n"
            "Atualmente, ele pode:\n"
        )

        for feature in features:
            description += f"- {feature}\n"

        if self.dev_mode:
            description += "\n O modo desenvolvedor está ATIVO."
        else:
            description += "\n O modo desenvolvedor está DESATIVADO."

        return description
        