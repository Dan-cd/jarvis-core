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
    # Config global
    bootstrap_env()
    Config.validate()

    # Context
    context = ExecutionContext()

    # Plugins (carrega todos)
    load_plugins()

    # Modelos de linguagem
    primary_llm = GroqLLM(config={"api_key": Config.GROQ_API_KEY})
    fallback_llm = OllamaLLM(config={"model": Config.OLLAMA_MODEL})

    llm_manager = LLMManager(primary_llm=primary_llm, fallback_llm=fallback_llm)

    # Router e Executor
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

    jarvis = Jarvis(
        router=router,
        executor=executor,
        answer_pipeline=answer_pipeline,
        llm_manager=llm_manager,
        config=Config(),
    )

    jarvis.start()

if __name__ == "__main__":
    main()
