from Jarvis.core.bootstrap import bootstrap_env
bootstrap_env()

from Jarvis.core.context import ExecutionContext

ExecutionContext()

from groq import Groq
from Jarvis.core.memory import Memory
from Jarvis.core.LLMManager import LLMManager
from Jarvis.core.router import Router
from Jarvis.core.context import ExecutionContext
from Jarvis.core.main import Jarvis
from Jarvis.modules.llm.groq import GroqLLM
from Jarvis.modules.llm.ollama import OllamaLLM
from Jarvis.core.config import Config
from Jarvis.core.output_formatter import OutputFormatter
from Jarvis.core.executor import Executor
from Jarvis.core.answer_pipeline import AnswerPipeline
from Jarvis.sandbox import SandboxHandler
sandbox = SandboxHandler()

Config.validate()

context = ExecutionContext()
memory = Memory()

groq_client = Groq(api_key=Config.GROQ_API_KEY)

primary_llm = GroqLLM(client=groq_client)
fallback_llm = OllamaLLM(model="phi")

llm_manager = LLMManager(
    primary_llm=primary_llm
)


router = Router(
    context=context,
    sandbox=sandbox,
    memory=memory,
)

executor = Executor(
    llm=llm_manager,
    fallback=fallback_llm,
    sandbox=sandbox,
    memory=memory,
    context=context,
    answer_pipeline=AnswerPipeline(llm_manager)
)

def main():
    jarvis = Jarvis(
    router=router,
    executor=executor,
    output_formatter=OutputFormatter(context),
    context=context
)
    jarvis.start()

if __name__ == "__main__":
    main()


