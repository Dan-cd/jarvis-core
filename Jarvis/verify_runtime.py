import sys
import os

# Adiciona o diretório raiz ao python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from Jarvis.core.decision import Decision, DecisionOutcome, DecisionPath
from Jarvis.core.LLMManager import LLMManager, LLMExecutionError

def test_decision_init():
    print("--- Teste Decision.__init__ ---")
    try:
        # Tenta criar Decision sem argumentos opcionais (que causava erro)
        d = Decision(outcome=DecisionOutcome.DENY, reason="Teste")
        print(f"✅ Decision criada com sucesso: {d}")
    except TypeError as e:
        print(f"❌ Erro ao criar Decision: {e}")
        raise

def test_llm_fallback():
    print("\n--- Teste LLM Fallback ---")
    
    class MockLLM:
        def __init__(self, fail=False):
            self.fail = fail
        def generate(self, prompt, mode="default"):
            if self.fail:
                raise Exception("Simulando erro do provider")
            return "Resposta Mock"

    # Caso 1: Primário falha, sem fallback (deve lançar erro legível)
    manager = LLMManager(primary_llm=MockLLM(fail=True), fallback_llm=None)
    try:
        manager.generate("teste")
    except LLMExecutionError as e:
        print(f"✅ Erro esperado capturado (sem fallback): {e}")

    # Caso 2: Primário falha, com fallback (deve funcionar)
    manager_fallback = LLMManager(primary_llm=MockLLM(fail=True), fallback_llm=MockLLM(fail=False))
    try:
        res = manager_fallback.generate("teste")
        print(f"✅ Fallback funcionou: {res}")
    except Exception as e:
        print(f"❌ Falha no fallback: {e}")
        raise

if __name__ == "__main__":
    test_decision_init()
    test_llm_fallback()
