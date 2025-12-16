import os
from datetime import datetime
from Jarvis.safe.safe_execution import safe_execute
from Jarvis.core.errors import JarvisError
from Jarvis.core.config import Config
from Jarvis.core.errors import ErrorManager
from Jarvis.core.logger import log_error

class Jarvis:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.error_manager = ErrorManager(self.config)
        self.comandos = {}

        print("[Jarvis] Inicializando...")
        self.registrar_comandos()

    def start(self):
        print("[Jarvis] Sistema iniciado.")
        self.main_loop()

    def main_loop(self):
        print("[Jarvis] Aguardando comandos... (digite 'exit' para encerrar)")

        while True:
            comando = input("> ").strip()

            if not comando:
                continue

            if comando.lower() in ("exit", "sair", "quit"):
                print("[Jarvis] Encerrando sistema...")
                break

            resposta = self.executar_comando(comando)
            self.exibir_resposta(resposta)


    def executar_comando(self, comando: str):
        partes = comando.split()
        nome = partes[0].lower()

        if nome not in self.comandos:
            return "Comando não reconhecido."

        resultado = self.comandos[nome](partes[1:])
        
        if isinstance(resultado, JarvisError):
            log_error(resultado)
            print("⚠️ Ocorreu um erro. Veja o log para detalhes.")
            return resultado

        return resultado

    def exibir_resposta(self, resposta):
        if isinstance(resposta, JarvisError):
            print(f"[Jarvis] {resposta.message}")
        else:
            print(f"[Jarvis] {resposta}")

    def registrar_comandos(self):
        self.comandos = {
            "hora": self.cmd_hora,
            "limpar": self.cmd_limpar,
            "eco": self.cmd_eco,
            "help": self.cmd_help,
        }


    @safe_execute(sensitive=False)
    def cmd_hora(self, args):
        return f"Agora são {datetime.now().strftime('%H:%M:%S')}"

    @safe_execute(sensitive=True)
    def cmd_limpar(self, args):
        os.system("cls" if os.name == "nt" else "clear")
        return "Tela limpa"

    @safe_execute(sensitive=False)
    def cmd_eco(self, args):
        return " ".join(args) if args else "Nada para repetir"

    @safe_execute(sensitive=False)
    def cmd_help(self, args):
        return "Comandos disponíveis: " + ", ".join(self.comandos.keys())