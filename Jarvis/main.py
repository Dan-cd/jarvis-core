from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from Jarvis.core.memory import Memory
from Jarvis.core.LLMManager import LLMManager
from Jarvis.core.answer_pipeline import AnswerPipeline
from Jarvis.core.router import Router
from Jarvis.core.context import ExecutionContext
from Jarvis.core.main import Jarvis
from Jarvis.modules.llm.groq import GroqLLM
from Jarvis.modules.llm.ollama import OllamaLLM
from Jarvis.core.config import Config

Config.validate()

context = ExecutionContext()
memory = Memory()

groq_client = Groq(api_key=Config.GROQ_API_KEY)

primary_llm = GroqLLM(client=groq_client)
fallback_llm = OllamaLLM(model="phi")

llm_manager = LLMManager(
    primary_llm=primary_llm
)

answer_pipeline = AnswerPipeline(llm_manager)

router = Router(
    llm_manager=llm_manager,
    sandbox=None,
    context=context,
    memory=memory,
    answer_pipeline=answer_pipeline
)

def main():
    jarvis = Jarvis(router=router)
    jarvis.start()

if __name__ == "__main__":
    main()


