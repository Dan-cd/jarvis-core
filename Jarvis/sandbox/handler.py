class SandboxHandler:
    def handle(self, decision, context):
        intent = decision.payload

        if intent is None:
            return "[JARVIS] Nenhuma ação executável para este comando."

        if intent.name == "dev.enter":
            context.dev_mode = True
            return "[JARVIS] Modo desenvolvedor ativado."

        if intent.name == "dev.exit":
            context.dev_mode = False
            return "[JARVIS] Modo desenvolvedor desativado."

        return "[JARVIS] Ação de sandbox não reconhecida."