from Jarvis.modules.llm.base import BaseLLM


class GroqLLM(BaseLLM):

    def __init__(self, client, model="llama3-70b-8192"):
        self.client = client
        self.model = model

        
    def generate(self, prompt: str, context: list) -> str:
        messages = context + [{"role": "user", "content": prompt}]

        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages
        )

        return response.choices[0].message.content