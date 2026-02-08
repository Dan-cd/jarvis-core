from Jarvis.core.config import Config

class DevModeManager:
    def __init__(self, context, config: Config):
        self.context = context
        self.config = config

    def enter(self, password: str) -> str:
        if self.context.dev_mode:
            return "Dev mode já está ativo."
        
        if password != self.config.JARVIS_DEV_PASSWORD:
            return "Senha incorreta. Acesso negado."
        
        self.context.dev_mode = True
        return "Dev mode ativado. Acesso avançado liberado."
    
    def exit(self) -> str:
        if not self.context.dev_mode:
            return "Dev mode não está ativo."
        self.context.dev_mode = False
        return "Dev mode desativado."

