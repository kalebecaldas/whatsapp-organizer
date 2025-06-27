# utils/gpt.py

import openai
from clients.openai_client import chat_with_functions

def gerar_resposta(mensagens):
    resposta = chat_with_functions(mensagens)
    return resposta


openai.api_key = "SUA_CHAVE_OPENAI"

def ask_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Erro ao consultar GPT: {e}")
        return "Desculpe, houve um erro ao processar sua solicitação."
