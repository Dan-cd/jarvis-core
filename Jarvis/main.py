
# Jarvis/main.py
from Jarvis.core.bootstrap import bootstrap_env
from Jarvis.core.config import Config
from Jarvis.core.context import ExecutionContext
from Jarvis.core.LLMManager import LLMManager
from Jarvis.core.router import Router
from Jarvis.core.main import Jarvis
from Jarvis.modules.llm.groq import GroqLLM
from Jarvis.modules.llm.ollama import OllamaLLM
from Jarvis.core.output_formatter import OutputFormatter
from Jarvis.core.executor import Executor
from Jarvis.core.answer_pipeline import AnswerPipeline
from Jarvis.plugins.loader import load_plugins


def main():
    # --- bootstrap e ambiente
    bootstrap_env()

    # --- instância de configuração (única fonte)
    config = Config()
    config.validate()  # não fatal por default; imprime avisos

    # --- contexto de execução
    context = ExecutionContext()
    context.dev_mode = config.dev_mode
    context.offline = config.offline

    # --- carregar plugins (registro global)
    load_plugins()

    # --- instanciar provedores LLM com robustez (Ollama = Baseline, Groq = Progressive Enhancement)
    primary_llm = None
    fallback_llm = None

    # 1. Tenta instanciar Ollama (Baseline garantido)
    ollama_instance = None
    if config.allow_llm:
        try:
            ollama_instance = OllamaLLM(config={"model": config.OLLAMA_MODEL})
        except Exception as e:
            print(f"[main] ⚠️ Falha crítica ao iniciar Ollama (Baseline): {e}")

    # 2. Tenta instanciar Groq (Melhoria opcional)
    groq_instance = None
    if config.GROQ_API_KEY and config.allow_llm:
        try:
            groq_instance = GroqLLM(config={"api_key": config.GROQ_API_KEY, "model": config.GROQ_MODEL})
        except Exception as e:
            print(f"[main] ⚠️ Groq indisponível (continuando com fallback): {e}")

    # 3. Define papeis (Primary vs Fallback)
    if groq_instance:
        primary_llm = groq_instance
        fallback_llm = ollama_instance # Se Groq cair, usa Ollama
        print(f"[main] LLM Primário: Groq ({config.GROQ_MODEL}) | Fallback: Ollama ({config.OLLAMA_MODEL})")
    elif ollama_instance:
        primary_llm = ollama_instance
        fallback_llm = None # Ollama já é o primário
        print(f"[main] LLM Primário: Ollama ({config.OLLAMA_MODEL}) | Sem fallback externo.")
    else:
        print("[main] ❌ ERRO: Nenhum LLM disponível. O sistema funcionará apenas com comandos locais.")

    llm_manager = LLMManager(primary_llm=primary_llm, fallback_llm=fallback_llm, context=context)

    # --- Router / Executor / AnswerPipeline
    router = Router(context)
    answer_pipeline = AnswerPipeline(context)
    executor = Executor(
        llm=llm_manager,
        fallback=None,
        sandbox=None,
        memory=None,
        execution_memory=context.execution_memory,
        temp_memory=context.temp_memory,
        context=context,
        answer_pipeline=answer_pipeline,
        dev_guard=None
    )

    formatter = OutputFormatter(context)

    # --- instância do Jarvis core (injeção de dependências)
    jarvis = Jarvis(
        router=router,
        executor=executor,
        answer_pipeline=answer_pipeline,
        llm_manager=llm_manager,
        config=config,
    )

    jarvis.start()


if __name__ == "__main__":
    main()
