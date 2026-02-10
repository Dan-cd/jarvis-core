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
        if not self.context.dev_mode:
            return "Ação permitida apenas em Dev Mode."

        path = params.get("path")
        if not path:
            return "Caminho inválido."

        # Define sandbox root
        sandbox_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/sandbox"))
        
        # Resolve target path
        # Se for absoluto, tenta usar relative para verificar se está dentro
        # Se for relativo, join com root
        try:
            target_path = os.path.abspath(os.path.join(sandbox_root, path))
            
            # Security check: target must be inside sandbox_root
            if not target_path.startswith(sandbox_root):
                return "Acesso negado: Arquivo fora do sandbox."
            
            if not os.path.exists(target_path):
                return "Arquivo não encontrado."

            if os.path.isdir(target_path):
                return "Diretórios não podem ser lidos."

            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(5000)
        except Exception as e:
            return f"Erro de segurança ou I/O: {e}"