from groq import Groq
from Jarvis.core.config import Config
from Jarvis.core.llm_router import LLMRouter
from Jarvis.core.policy import PolicyEngine
from Jarvis.modules.llm.groq import GroqLLM
from Jarvis.core.main import Jarvis

Config.validate()

groq_client = Groq(api_key=Config.GROQ_API_KEY)
llm = GroqLLM(client=groq_client)
policy = PolicyEngine(context=None)

router = LLMRouter(llm=llm, policy=policy)

def main():
    jarvis = Jarvis(router=router)
    jarvis.start()

if __name__ == "__main__":
    main()


