from dotenv import load_dotenv
from pathlib import Path
import os
import traceback
from groq import Groq

load_dotenv(dotenv_path=str(Path(__file__).resolve().parent / '.env'))
api_key = os.getenv('GROQ_API_KEY')
print('GROQ_API_KEY presente:', bool(api_key))

try:
    client = Groq(api_key=api_key)
    models = client.models.list()
    print('Modelos disponíveis retornados pela API:')
    for m in models.data:
        print('-', getattr(m, 'id', repr(m)))
except Exception as e:
    print('Erro ao listar modelos:', e)
    traceback.print_exc()
