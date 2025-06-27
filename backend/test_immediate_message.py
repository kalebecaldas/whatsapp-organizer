#!/usr/bin/env python3
"""
Script de teste para verificar se as mensagens do paciente são salvas e emitidas imediatamente
"""

import requests
import json
import time
from datetime import datetime

def test_immediate_message():
    """Testa se a mensagem do paciente aparece imediatamente"""
    
    # URL do webhook
    webhook_url = "http://localhost:5001/api/webhook"
    
    # Dados da mensagem
    message_data = {
        "from": "5511999999999",
        "body": f"Teste de mensagem imediata - {datetime.now().strftime('%H:%M:%S')}"
    }
    
    print(f"🔄 Enviando mensagem: {message_data['body']}")
    
    # Enviar mensagem
    start_time = time.time()
    response = requests.post(webhook_url, json=message_data)
    end_time = time.time()
    
    print(f"⏱️ Tempo de resposta: {end_time - start_time:.2f} segundos")
    print(f"📨 Resposta: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sucesso: {result.get('status')}")
        print(f"💬 Resposta do bot: {result.get('result')}")
    else:
        print(f"❌ Erro: {response.text}")
    
    # Verificar mensagens no banco
    print("\n🔍 Verificando mensagens no banco...")
    messages_url = "http://localhost:5001/api/messages"
    messages_response = requests.get(messages_url)
    
    if messages_response.status_code == 200:
        conversations = messages_response.json()
        for conv in conversations:
            if conv['phone'] == message_data['from']:
                print(f"📱 Conversa encontrada: {conv['phone']}")
                print(f"📨 Total de mensagens: {len(conv['messages'])}")
                
                # Mostrar as últimas 3 mensagens
                for i, msg in enumerate(conv['messages'][-3:], 1):
                    print(f"  {i}. {msg['from']}: {msg['text']} ({msg['timestamp']})")
                break
    else:
        print(f"❌ Erro ao buscar mensagens: {messages_response.text}")

if __name__ == "__main__":
    test_immediate_message() 