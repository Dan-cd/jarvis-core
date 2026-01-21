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

    # --- instanciar provedores LLM com dados vindos da config
    primary_llm = None
    fallback_llm = None

    # Se houver API key Groq, cria o GroqLLM (padrão)
    if config.GROQ_API_KEY and config.allow_llm:
        try:
            primary_llm = GroqLLM(config={"api_key": config.GROQ_API_KEY, "model": config.GROQ_MODEL})
        except Exception as e:
            print(f"[main] Falha ao iniciar GroqLLM: {e}")

    # Sempre criamos um Ollama local (fallback) se permitido
    if config.allow_llm:
        try:
            fallback_llm = OllamaLLM(config={"model": config.OLLAMA_MODEL})
        except Exception as e:
            print(f"[main] Falha ao iniciar OllamaLLM: {e}")

    llm_manager = LLMManager(primary_llm=primary_llm, fallback_llm=fallback_llm, context=context)

    # --- Router / Executor / AnswerPipeline
    router = Router(context)
    answer_pipeline = AnswerPipeline(context)
    executor = Executor(
        llm=llm_manager,
        fallback=None,
        sandbox=None,
        memory=None,
        execution_memory=None,
        temp_memory=None,
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
