from dataclasses import dataclass

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
    
@dataclass
class IntentResult:
    name: str
    confidence: float
    raw_text: str
