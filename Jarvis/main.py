from Jarvis.core.bootstrap import bootstrap_env
bootstrap_env()

from Jarvis.core.context import ExecutionContext

ExecutionContext()
import Jarvis.plugins_available.filesystem
from groq import Groq
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
from Jarvis.core.dev_mode_guard import DevModeGuard
from Jarvis.core.memory.store import MemoryStore
from Jarvis.core.memory.manager import MemoryManager
from Jarvis.core.memory.models import MemoryType
from Jarvis.core.dev_mode_guard import DevModeGuard
from Jarvis.plugins.loader import load_plugins
load_plugins()

dev_guard = DevModeGuard(
    password=Config.DEV_MODE_PASSWORD
)

memory_store = MemoryStore()
memory_manager = MemoryManager(memory_store)

# EXEMPLO DE USO (mais tarde vem do Intent + Router)
user_explicitly_requested = True


Config.validate()

context = ExecutionContext()
sandbox = SandboxHandler(context)
memory_manager = MemoryManager(memory_store)

groq_client = Groq(api_key=Config.GROQ_API_KEY)

primary_llm = GroqLLM()
fallback_llm = OllamaLLM(model="phi")

llm_manager = LLMManager()


router = Router(
    context=context
)

executor = Executor(
    llm=llm_manager,
    fallback=fallback_llm,
    sandbox=sandbox,
    memory=memory_manager,
    context=context,
    answer_pipeline=AnswerPipeline(llm_manager),
    dev_guard=dev_guard
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


