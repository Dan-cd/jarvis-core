import os


class SandboxHandler:

    def __init__(self, context):
        self.context = context

    def handle(self):
        self.context.dev_mode = False
        return "Modo desenvolvedor desativado."
    
    def execute_action(self, action, memory):
        action_name = action["action"]
        params = action["params"]

        if action_name == "filesystem.read":
            return self._read_file(params)

        return "Ação não reconhecida no sandbox."

    def _read_file(self, params):
        path = params.get("path")

        if not path:
            return "Caminho inválido."

        if not os.path.exists(path):
            return "Arquivo não encontrado."

        if os.path.isdir(path):
            return "Diretórios não podem ser lidos."

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(5000)  # limite de segurança
        except Exception as e:
            return f"Erro ao ler arquivo: {e}"