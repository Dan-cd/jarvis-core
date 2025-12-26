class SandboxHandler:

    def __init__(self, context):
        self.context = context

    def handle(self):
        self.context.dev_mode = False
        return "Modo desenvolvedor desativado."