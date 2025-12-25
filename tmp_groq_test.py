from dotenv import load_dotenv
from pathlib import Path
import os
import traceback
from groq import Groq

# carregar .env do projeto
load_dotenv(dotenv_path=str(Path(__file__).resolve().parent / '.env'))

api_key = os.getenv('GROQ_API_KEY')
model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
print('GROQ_API_KEY presente:', bool(api_key))
print('Usando modelo:', model)

try:
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Diga olá e calcule 2+2."}]
    )
    print('RESPOSTA DO GROQ:')
    print(resp.choices[0].message.content)
except Exception as e:
    print('ERRO AO CHAMAR GROQ:', e)
    traceback.print_exc()
