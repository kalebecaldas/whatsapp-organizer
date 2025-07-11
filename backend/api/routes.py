from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from handlers.message_handler import handle_message
from collections import defaultdict
import re
from message_store import messages_store
from database import db
from flask_socketio import emit
from datetime import datetime
import json
import logging
import requests

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)

# Global variable to store socketio instance
socketio = None

def init_socketio(sio):
    global socketio
    socketio = sio

def emit_message_update():
    """Função auxiliar para emitir atualização de mensagens via WebSocket"""
    if not socketio:
        return
        
    try:
        # Get updated conversations
        all_messages = db.get_messages(limit=1000)
        conversations = {}
        
        for msg in all_messages:
            phone_num = msg['phone_number']
            if phone_num not in conversations:
                conversations[phone_num] = {
                    'phone': phone_num,
                    'messages': [],
                    'last_message': '',
                    'last_timestamp': None
                }
            
            conversations[phone_num]['messages'].append({
                'id': msg['id'],
                'from': msg['from'],
                'text': msg['message_text'],
                'timestamp': msg['timestamp'],
                'direction': msg['direction']
            })
            
            if not conversations[phone_num]['last_timestamp'] or msg['timestamp'] > conversations[phone_num]['last_timestamp']:
                conversations[phone_num]['last_message'] = msg['message_text']
                conversations[phone_num]['last_timestamp'] = msg['timestamp']
        
        conversations_list = list(conversations.values())
        conversations_list.sort(key=lambda x: x['last_timestamp'] or '', reverse=True)
        
        logger.info(f"📊 Conversas agrupadas: {len(conversations_list)} conversas")
        socketio.emit('message_update', {'conversations': conversations_list})
        logger.info("✅ Evento 'message_update' emitido via WebSocket")
        
    except Exception as e:
        logger.error(f"❌ Erro ao emitir WebSocket: {e}")

# Função para formatar número de telefone
def format_phone_number(phone):
    """Formata o número de telefone para exibição"""
    # Remove todos os caracteres não numéricos
    digits = re.sub(r'\D', '', str(phone))
    
    # Se começa com 55 (Brasil), formata como +55 XX XXXXX-XXXX
    if digits.startswith('55') and len(digits) >= 13:
        return f"+{digits[:2]} {digits[2:4]} {digits[4:9]}-{digits[9:13]}"
    
    # Se tem 11 dígitos (com DDD), formata como +55 XX XXXXX-XXXX
    elif len(digits) == 11:
        return f"+55 {digits[:2]} {digits[2:7]}-{digits[7:11]}"
    
    # Se tem 10 dígitos (com DDD), formata como +55 XX XXXX-XXXX
    elif len(digits) == 10:
        return f"+55 {digits[:2]} {digits[2:6]}-{digits[6:10]}"
    
    # Caso contrário, retorna como está
    return str(phone)

# Função para gerar avatar baseado no número
def generate_avatar(phone):
    """Gera um avatar baseado no número de telefone"""
    digits = re.sub(r'\D', '', str(phone))
    last_two = digits[-2:] if len(digits) >= 2 else digits
    return f"https://api.dicebear.com/7.x/initials/svg?seed={last_two}&backgroundColor=25D366&textColor=FFFFFF"

# Função para extrair nome do número (simulação)
def extract_name_from_phone(phone):
    """Extrai um nome baseado no número (simulação)"""
    # Em um sistema real, isso viria de uma base de dados de contatos
    # Por enquanto, vamos simular alguns nomes baseados no número
    
    digits = re.sub(r'\D', '', str(phone))
    last_four = digits[-4:] if len(digits) >= 4 else digits
    
    # Simulação de nomes baseados nos últimos dígitos
    name_mapping = {
        '1234': 'João Silva',
        '5678': 'Maria Santos',
        '9012': 'Pedro Costa',
        '3456': 'Ana Oliveira',
        '7890': 'Carlos Lima',
        '2345': 'Lucia Ferreira',
        '6789': 'Roberto Alves',
        '0123': 'Fernanda Rocha',
        '4567': 'Marcos Pereira',
        '8901': 'Juliana Souza'
    }
    
    return name_mapping.get(last_four, None)

@api_bp.route("/webhook", methods=["GET", "POST"])
@cross_origin()
def webhook():
    if request.method == "GET":
        return "Webhook ativo com Venom Bot", 200

    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição inválida"}), 400

    from_number = data.get("from", "")
    incoming_msg = data.get("body", "").strip()
    print(f"🔔 Mensagem recebida de {from_number}: {incoming_msg}")

    # PRIMEIRO: Salvar mensagem do usuário imediatamente e emitir WebSocket
    db.save_message(from_number, incoming_msg, "received", "user")
    
    # Emitir WebSocket imediatamente para mostrar a mensagem do usuário
    logger.info("🔔 Emitindo mensagem do usuário via WebSocket...")
    emit_message_update()
    logger.info("✅ Mensagem do usuário emitida via WebSocket")

    # SEGUNDO: Processar resposta do bot (pode demorar)
    reply_text = handle_message(from_number, incoming_msg) or "Desculpe, não entendi."
    print(f"💬 Resposta gerada: {reply_text}")

    # TERCEIRO: Salvar resposta do bot e emitir WebSocket novamente
    if reply_text:
        db.save_message(from_number, reply_text, "sent", "agent")
        
        # Emitir WebSocket novamente para mostrar a resposta do bot
        logger.info("🔔 Emitindo resposta do bot via WebSocket...")
        emit_message_update()
        logger.info("✅ Resposta do bot emitida via WebSocket")

    return jsonify({"result": reply_text, "status": "ok"}), 200

@api_bp.route("/messages", methods=["GET"])
@cross_origin()
def get_messages():
    """Get all messages grouped by phone number"""
    try:
        # Get all messages from database
        all_messages = db.get_messages(limit=1000)
        
        # Group messages by phone number
        conversations = {}
        for msg in all_messages:
            phone = msg['phone_number']
            if phone not in conversations:
                conversations[phone] = {
                    'phone': phone,
                    'messages': [],
                    'last_message': '',
                    'last_timestamp': None
                }
            
            # Add message to conversation
            conversations[phone]['messages'].append({
                'id': msg['id'],
                'from': msg['from'],
                'text': msg['message_text'],
                'timestamp': msg['timestamp'],
                'direction': msg['direction']
            })
            
            # Update last message info
            if not conversations[phone]['last_timestamp'] or msg['timestamp'] > conversations[phone]['last_timestamp']:
                conversations[phone]['last_message'] = msg['message_text']
                conversations[phone]['last_timestamp'] = msg['timestamp']
        
        # Ordenar as mensagens de cada conversa do mais antigo para o mais novo
        for conv in conversations.values():
            conv['messages'].sort(key=lambda m: m['timestamp'])
        
        # Convert to list and sort by last timestamp
        conversations_list = list(conversations.values())
        conversations_list.sort(key=lambda x: x['last_timestamp'] or '', reverse=True)
        
        logger.info(f"📊 Conversas agrupadas: {len(conversations_list)} conversas")
        return jsonify(conversations_list)
        
    except Exception as e:
        logger.error(f"❌ Error getting messages: {e}")
        return jsonify([]), 500

@api_bp.route("/messages/<phone>", methods=["GET"])
@cross_origin()
def get_messages_by_phone(phone):
    """Get messages for a specific phone number"""
    try:
        messages = db.get_messages_by_phone(phone, limit=100)
        
        # Format messages for frontend
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'id': msg['id'],
                'from': msg['from'],
                'text': msg['message_text'],
                'timestamp': msg['timestamp'],
                'direction': msg['direction']
            })
        
        return jsonify(formatted_messages)
        
    except Exception as e:
        logger.error(f"❌ Error getting messages for {phone}: {e}")
        return jsonify([]), 500

@api_bp.route("/send-message", methods=["POST"])
@cross_origin()
def send_message():
    """Send a message from the panel"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            return jsonify({'error': 'Phone and message are required'}), 400
        
        # Primeiro, tenta enviar a mensagem via Venom Bot
        try:
            venom_response = requests.post(
                'http://localhost:3000/send-message',
                json={'phone': phone, 'message': message},
                timeout=30
            )
            
            if venom_response.status_code == 200:
                logger.info(f"📤 Mensagem enviada com sucesso via Venom Bot para {phone}")
            else:
                logger.error(f"❌ Erro ao enviar via Venom Bot: {venom_response.status_code} - {venom_response.text}")
                return jsonify({'error': 'Failed to send message via WhatsApp'}), 500
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erro de conexão com Venom Bot: {e}")
            return jsonify({'error': 'Venom Bot not available'}), 503
        
        # Se chegou até aqui, a mensagem foi enviada com sucesso
        # Agora salva no banco de dados
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        success = db.save_message(
            phone_number=phone,
            message_text=message,
            direction='sent',
            from_field='agent',
            timestamp=timestamp
        )
        
        if success:
            # Emit WebSocket update
            logger.info("🔔 Emitindo atualização de mensagens via WebSocket...")
            emit_message_update()
            
            return jsonify({'success': True, 'message': 'Message sent successfully'})
        else:
            return jsonify({'error': 'Failed to save message'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route("/stats", methods=["GET"])
@cross_origin()
def get_stats():
    """Get message statistics"""
    try:
        stats = db.get_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        return jsonify({
            'total_messages': 0,
            'messages_today': 0,
            'unique_phones': 0,
            'direction_stats': {}
        }), 500

@api_bp.route("/clear-messages", methods=["POST"])
@cross_origin()
def clear_messages():
    """Clear all messages (for testing)"""
    try:
        success = db.clear_messages()
        if success:
            # Emit WebSocket update
            emit_message_update()
            
            return jsonify({'success': True, 'message': 'All messages cleared'})
        else:
            return jsonify({'error': 'Failed to clear messages'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error clearing messages: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route("/migrate-messages", methods=["POST"])
@cross_origin()
def migrate_messages():
    """Migrate old messages from Redis or other format"""
    try:
        data = request.get_json()
        old_messages = data.get('messages', [])
        
        success = db.migrate_old_messages(old_messages)
        
        if success:
            # Emit WebSocket update after migration
            emit_message_update()
            
            return jsonify({'success': True, 'message': f'Migrated {len(old_messages)} messages'})
        else:
            return jsonify({'error': 'Failed to migrate messages'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error migrating messages: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/test-bot', methods=['POST'])
@cross_origin()
def test_bot():
    data = request.get_json()
    numero = data.get('numero')
    mensagem = data.get('mensagem')
    if not numero or not mensagem:
        return jsonify({'erro': 'Número e mensagem são obrigatórios.'}), 400
    resposta = handle_message(numero, mensagem)
    return jsonify({'resposta': resposta})
