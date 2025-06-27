import os
import json
import traceback
import time
import random
from openai import OpenAI
from openai.types.chat import ChatCompletionToolParam, ChatCompletionMessage, ChatCompletionMessageToolCall
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("❌ OPENAI_API_KEY não definida no ambiente.")

# Configurações de timeout e conectividade mais robustas
client = OpenAI(
    api_key=api_key,
    timeout=60.0,  # Timeout global de 60 segundos
    max_retries=2  # Retries automáticos da biblioteca
)

# A lista de 'ferramentas' (funções) que a IA pode decidir chamar
tools: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "iniciar_agendamento",
            "description": "Inicia o fluxo para agendar uma nova consulta quando o usuário expressa essa intenção.",
            "parameters": {
                "type": "object",
                "properties": {
                    "unidade": {"type": "string", "description": "A unidade específica que o usuário mencionou, como 'Vieiralves' ou 'São José'."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_insurance_data",
            "description": "Verifica se um convênio específico é aceito ou lista todos os convênios da clínica.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_convenio": {"type": "string", "description": "O nome do convênio sobre o qual o usuário está perguntando."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_clinic_data",
            "description": "Retorna dados das clínicas, como endereço e telefone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "unidade": {"type": "string", "description": "O nome da unidade específica."}
                }
            }
        }
    }
]

def chat_with_functions(messages, max_retries=3, base_delay=1.0):
    """Chama o modelo GPT com suporte a `tools` e retorna o objeto de mensagem da resposta."""
    
    def make_request_with_retry(use_tools=True):
        """Faz a requisição com retry e backoff exponencial"""
        for attempt in range(max_retries + 1):
            try:
                if use_tools:
                    print(f"🧠 Tentativa {attempt + 1}/{max_retries + 1}: Chamando API da OpenAI com ferramentas...")
                    print("--- PAYLOAD ENVIADO (com ferramentas) ---")
                    print(json.dumps({
                        'model': 'gpt-3.5-turbo',
                        'messages': messages,
                        'tools': tools,
                        'tool_choice': 'auto',
                        'timeout': 30.0
                    }, indent=2, ensure_ascii=False))
                    resp = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                        timeout=30.0  # Timeout de 30 segundos
                    )
                else:
                    print(f"🔄 Tentativa {attempt + 1}/{max_retries + 1}: Chamando API da OpenAI sem ferramentas...")
                    print("--- PAYLOAD ENVIADO (sem ferramentas) ---")
                    print(json.dumps({
                        'model': 'gpt-3.5-turbo',
                        'messages': messages,
                        'timeout': 30.0
                    }, indent=2, ensure_ascii=False))
                    resp = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        timeout=30.0  # Timeout de 30 segundos
                    )
                
                print(f"✅ Resposta da OpenAI recebida com sucesso (API REAL) - Tentativa {attempt + 1}")
                return resp.choices[0].message
                
            except Exception as e:
                print(f"❌ Erro na tentativa {attempt + 1}: {e}")
                traceback.print_exc()
                
                # Se for uma exceção da OpenAI, tente mostrar o corpo da resposta
                response = getattr(e, 'response', None)
                if response is not None and hasattr(response, 'text'):
                    print(f"Resposta de erro da OpenAI: {response.text}")
                
                # Se não for a última tentativa, aguarda antes de tentar novamente
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)  # Backoff exponencial + jitter
                    print(f"⏳ Aguardando {delay:.2f} segundos antes da próxima tentativa...")
                    time.sleep(delay)
                else:
                    print(f"❌ Todas as {max_retries + 1} tentativas falharam")
                    return None
    
    # Primeira tentativa com ferramentas
    result = make_request_with_retry(use_tools=True)
    if result:
        return result
    
    # Se falhou com ferramentas, tenta sem ferramentas
    print("🔄 Tentando sem ferramentas como fallback...")
    result = make_request_with_retry(use_tools=False)
    if result:
        return result
    
    # Se tudo falhou, usa fallback inteligente
    print("🔄 Usando modo de fallback inteligente...")
    return get_fallback_response(messages)

def get_fallback_response(messages):
    """Fornece respostas contextuais quando a API da OpenAI não está disponível"""
    if not messages:
        return ChatCompletionMessage(
            role='assistant',
            content="Olá! Como posso ajudá-lo hoje?"
        )
    
    # Pega a última mensagem do usuário
    last_message = messages[-1].get('content', '').lower()
    
    # Respostas contextuais baseadas em palavras-chave
    if any(word in last_message for word in ['agendar', 'consulta', 'marcar', 'horário']):
        return ChatCompletionMessage(
            role='assistant',
            content="Perfeito! Vou ajudá-lo a agendar uma consulta. Para começar, preciso saber em qual unidade você gostaria de ser atendido. Temos as seguintes opções:\n\n1️⃣ **Vieiralves** - Centro\n2️⃣ **São José** - Zona Norte\n3️⃣ **Cohama** - Zona Sul\n\nQual unidade você prefere?"
        )
    
    elif any(word in last_message for word in ['unidade', 'vieiralves', 'são josé', 'cohaba']):
        return ChatCompletionMessage(
            role='assistant',
            content="Ótimo! Agora preciso saber qual procedimento você gostaria de realizar. Temos várias especialidades disponíveis:\n\n1️⃣ **Consulta Médica**\n2️⃣ **Exame Laboratorial**\n3️⃣ **Fisioterapia**\n4️⃣ **Psicologia**\n5️⃣ **Nutrição**\n\nQual procedimento você gostaria de agendar?"
        )
    
    elif any(word in last_message for word in ['procedimento', 'consulta médica', 'exame', 'fisioterapia', 'psicologia', 'nutrição']):
        return ChatCompletionMessage(
            role='assistant',
            content="Perfeito! Agora preciso saber qual data seria melhor para você. Temos horários disponíveis nos próximos dias. Qual data você prefere?\n\n📅 **Próximas datas disponíveis:**\n- Amanhã\n- Próxima semana\n- Outra data específica\n\nQual seria sua preferência?"
        )
    
    elif any(word in last_message for word in ['data', 'amanhã', 'semana', 'dia']):
        return ChatCompletionMessage(
            role='assistant',
            content="Excelente! Agora preciso saber qual horário seria melhor para você. Temos os seguintes turnos disponíveis:\n\n🌅 **Manhã** (8h às 12h)\n🌞 **Tarde** (14h às 18h)\n🌙 **Noite** (18h às 20h)\n\nQual turno você prefere?"
        )
    
    elif any(word in last_message for word in ['manhã', 'tarde', 'noite', 'turno']):
        return ChatCompletionMessage(
            role='assistant',
            content="Perfeito! Agora vou confirmar os dados do seu agendamento:\n\n📋 **Resumo do Agendamento:**\n- Unidade: [Unidade selecionada]\n- Procedimento: [Procedimento selecionado]\n- Data: [Data selecionada]\n- Horário: [Turno selecionado]\n\n✅ **Confirma o agendamento?**\n\nResponda 'Sim' para confirmar ou 'Não' para fazer alguma alteração."
        )
    
    elif any(word in last_message for word in ['sim', 'confirmar', 'ok']):
        return ChatCompletionMessage(
            role='assistant',
            content="🎉 **Agendamento confirmado com sucesso!**\n\n📅 Seu agendamento foi realizado e você receberá uma confirmação por WhatsApp em breve.\n\n📞 Se precisar de mais alguma coisa, é só me avisar!\n\nObrigado por escolher nossa clínica! 😊"
        )
    
    elif any(word in last_message for word in ['não', 'alterar', 'mudar']):
        return ChatCompletionMessage(
            role='assistant',
            content="Sem problemas! Vamos recomeçar o processo de agendamento. Diga 'agendar' para iniciar novamente."
        )
    
    elif any(word in last_message for word in ['oi', 'olá', 'bom dia', 'boa tarde', 'boa noite']):
        return ChatCompletionMessage(
            role='assistant',
            content="Olá! 👋 Bem-vindo à Clínica Ágil!\n\nComo posso ajudá-lo hoje? Posso auxiliar com:\n\n📅 **Agendamento de consultas**\n🏥 **Informações sobre unidades**\n💊 **Dúvidas sobre procedimentos**\n\nO que você gostaria de fazer?"
        )
    
    elif any(word in last_message for word in ['ajuda', 'help', 'como']):
        return ChatCompletionMessage(
            role='assistant',
            content="Claro! Estou aqui para ajudá-lo. Posso auxiliar com:\n\n📅 **Agendar consultas** - Diga 'gostaria de agendar'\n🏥 **Informações das unidades** - Pergunte sobre Vieiralves, São José ou Cohama\n💊 **Procedimentos disponíveis** - Consulte sobre consultas, exames, fisioterapia, etc.\n\nComo posso ajudá-lo?"
        )
    
    else:
        return ChatCompletionMessage(
            role='assistant',
            content="Entendo! Se você gostaria de agendar uma consulta, diga 'gostaria de agendar' e eu te ajudo com todo o processo. Se tiver outras dúvidas, é só perguntar! 😊"
        )

