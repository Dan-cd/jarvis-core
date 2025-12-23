from dataclasses import dataclass
from enum import Enum
from Jarvis.core.types import IntentType


@dataclass
class Intent:
    def __init__(self, name: str, raw: str = ""):
        self.name = name
        self.raw = raw 

class IntentEngine:
    def parse(self, text: str) -> Intent | None:
        text = text.lower().strip()

        if "dev" in text and ("enter" in text or "entrar" in text):
            return Intent(name="dev.enter")
        if "plugin" in text and "create" in text:
            return Intent(name="dev.create_plugin")
        INTENTS = {
        "entrar no dev mode": "dev.enter",
        "sair do dev mode": "dev.exit",
        "criar plugin": "dev.create_plugin",
        }

        if text in INTENTS:
            return Intent(
                name=INTENTS[text],
                raw=text
            )

        if "dev" in text and ("exit" in text or "sair" in text):
            return Intent(name="dev.exit")

        if text in ("help", "ajuda"):
            return Intent(name="help")

        return None
    def classify(self, user_input: str):
        text = user_input.lower()

        if any(kw in text for kw in ["lembra", "lembrar", "memória", "recorda", "recordar", "ultima conversa"]):
            return IntentType.MEMORY_QUERY
        
        if text in ("ajuda", "help", "o que você pode fazer", "quais são suas capacidades", "como funciona"):
            return IntentType.SYSTEM_HELP
        return IntentType.UNKNOWN
    
@dataclass
class IntentResult:
    name: str
    confidence: float
    raw_text: str
