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
import os
from werkzeug.utils import secure_filename
from session_store import get_session, set_session

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)

# Global variable to store socketio instance
socketio = None

def init_socketio(sio):
    global socketio
    socketio = sio

# Variável global para controlar debounce
_last_emit_time = 0

def emit_message_update():
    """Função auxiliar para emitir atualização de mensagens via WebSocket"""
    global _last_emit_time
    
    if not socketio:
        return
    
    # Debounce para evitar múltiplas emissões em sequência
    import time
    current_time = time.time()
    if current_time - _last_emit_time < 1.0:  # 1 segundo de debounce
        logger.info("⏸️ Debounce: ignorando emissão muito rápida")
        return
    _last_emit_time = current_time
        
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
                    'last_timestamp': None,
                    'transferido_humano': False,  # Default value
                    'dados_transferencia': None
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
        
        # Check for transfer data in session store
        for phone in conversations:
            session_data = get_session(phone)
            logger.info(f"📋 Verificando sessão para {phone}: {session_data}")
            
            # Garantir que os campos sempre existam
            conversations[phone]['transferido_humano'] = False  # Default
            conversations[phone]['atribuido_para'] = None  # Default
            conversations[phone]['dados_transferencia'] = None  # Default
            
            if session_data and session_data.get('dados', {}).get('transferido_humano'):
                conversations[phone]['transferido_humano'] = True
                conversations[phone]['dados_transferencia'] = session_data.get('dados', {}).get('dados_transferencia')
                conversations[phone]['atribuido_para'] = session_data.get('dados', {}).get('atribuido_para')
                logger.info(f"✅ Conversa {phone} transferida para humano: {conversations[phone]['transferido_humano']}, atribuída para: {conversations[phone]['atribuido_para']}")
            else:
                logger.info(f"📝 Conversa {phone} permanece no bot (não transferida)")
        
        # Adicionar campos obrigatórios para cada conversa
        for conv in conversations.values():
            conv['id'] = conv['phone']  # Garantir que id existe
            conv['name'] = extract_name_from_phone(conv['phone']) or f"Paciente {conv['phone']}"
            conv['avatar'] = generate_avatar(conv['phone'])
            conv['formattedPhone'] = format_phone_number(conv['phone'])
            conv['originalName'] = extract_name_from_phone(conv['phone'])
            
            # Garantir que os campos de transferência sempre existam
            if 'transferido_humano' not in conv:
                conv['transferido_humano'] = False
            if 'atribuido_para' not in conv:
                conv['atribuido_para'] = None
            if 'dados_transferencia' not in conv:
                conv['dados_transferencia'] = None
        
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

@api_bp.route('/global-queue', methods=['GET'])
@cross_origin()
def get_global_queue():
    """Get conversations transferred by bot (not yet assigned to human)"""
    try:
        # Get all messages from database
        all_messages = db.get_messages(limit=1000)
        
        # Group messages by phone number
        conversations = {}
        for msg in all_messages:
            phone = msg['phone_number']
            if phone not in conversations:
                conversations[phone] = {
                    'id': phone,
                    'phone': phone,
                    'messages': [],
                    'last_message': '',
                    'last_timestamp': None,
                    'transferido_humano': False,
                    'atribuido_para': None,
                    'dados_transferencia': None
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
        
        # Check for transfer data in session store
        global_queue = []
        for phone in conversations:
            session_data = get_session(phone)
            if session_data and session_data.get('dados', {}).get('transferido_humano'):
                conversations[phone]['transferido_humano'] = True
                conversations[phone]['dados_transferencia'] = session_data.get('dados', {}).get('dados_transferencia')
                
                # Only add to global queue if not assigned to any user
                if not conversations[phone].get('atribuido_para'):
                    global_queue.append(conversations[phone])
        
        # Sort by timestamp (oldest first for queue)
        global_queue.sort(key=lambda x: x['last_timestamp'] or '', reverse=False)
        
        logger.info(f"🌍 Global queue: {len(global_queue)} conversations")
        return jsonify(global_queue)
        
    except Exception as e:
        logger.error(f"❌ Error getting global queue: {e}")
        return jsonify([]), 500

@api_bp.route('/assign-conversation', methods=['POST'])
@cross_origin()
def assign_conversation():
    """Assign a conversation to a specific user"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversationId')
        user_id = data.get('userId')
        
        if not conversation_id or not user_id:
            return jsonify({'error': 'conversationId and userId are required'}), 400
        
        logger.info(f"📋 Assigning conversation {conversation_id} to user {user_id}")
        
        # Get session data for this conversation
        session_data = get_session(conversation_id)
        
        if session_data:
            # Update session to assign the conversation to the user
            if 'dados' not in session_data:
                session_data['dados'] = {}
            
            session_data['dados']['transferido_humano'] = True
            session_data['dados']['atribuido_para'] = user_id
            
            # Save updated session
            set_session(conversation_id, session_data)
            
            logger.info(f"✅ Conversation {conversation_id} assigned to user {user_id}")
            return jsonify({'success': True, 'message': 'Conversation assigned successfully'})
        else:
            logger.warning(f"⚠️ No session found for conversation {conversation_id}")
            return jsonify({'error': 'No session found for this conversation'}), 404
        
    except Exception as e:
        logger.error(f"❌ Error assigning conversation: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/transfer-conversation', methods=['POST'])
@cross_origin()
def transfer_conversation():
    """Transfer a conversation from bot to human queue"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversationId')
        user_id = data.get('userId')
        
        if not conversation_id:
            return jsonify({'error': 'conversationId is required'}), 400
        
        logger.info(f"🔄 Transferring conversation {conversation_id} to human queue")
        
        # Get the phone number from the conversation ID (assuming it's the phone)
        phone = conversation_id
        
        # Get session data for this conversation
        session_data = get_session(phone)
        
        if session_data:
            # Update session to mark as transferred to human and assigned to user
            if 'dados' not in session_data:
                session_data['dados'] = {}
            
            session_data['dados']['transferido_humano'] = True
            session_data['dados']['atribuido_para'] = user_id  # Assign to current user
            
            # Save updated session
            set_session(phone, session_data)
            
            logger.info(f"✅ Conversation {conversation_id} transferred to human queue and assigned to user {user_id}")
            return jsonify({'success': True, 'message': 'Conversation transferred successfully'})
        else:
            logger.warning(f"⚠️ No session found for conversation {conversation_id}")
            return jsonify({'error': 'No session found for this conversation'}), 404
        
    except Exception as e:
        logger.error(f"❌ Error transferring conversation: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/return-to-global-queue', methods=['POST'])
@cross_origin()
def return_to_global_queue():
    """Return a conversation to the global queue"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversationId')
        phone = data.get('phone')
        
        if not conversation_id or not phone:
            return jsonify({'error': 'conversationId and phone are required'}), 400
        
        logger.info(f"🔄 Returning conversation {conversation_id} to global queue")
        
        # Get session data for this conversation
        session_data = get_session(phone)
        
        if session_data:
            # Update session to mark as transferred to human but not assigned
            if 'dados' not in session_data:
                session_data['dados'] = {}
            
            session_data['dados']['transferido_humano'] = True
            session_data['dados']['atribuido_para'] = None  # Remove assignment
            
            # Save updated session
            set_session(phone, session_data)
            
            logger.info(f"✅ Conversation {conversation_id} returned to global queue")
            return jsonify({'success': True, 'message': 'Conversation returned to global queue successfully'})
        else:
            logger.warning(f"⚠️ No session found for conversation {conversation_id}")
            return jsonify({'error': 'No session found for this conversation'}), 404
        
    except Exception as e:
        logger.error(f"❌ Error returning conversation to global queue: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/add-to-global-queue', methods=['POST'])
@cross_origin()
def add_to_global_queue():
    """Add a conversation to the global queue"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversationId')
        phone = data.get('phone')
        
        if not conversation_id or not phone:
            return jsonify({'error': 'conversationId and phone are required'}), 400
        
        logger.info(f"🔄 Adding conversation {conversation_id} to global queue")
        
        # Get session data for this conversation
        session_data = get_session(phone)
        
        if session_data:
            # Update session to mark as transferred to human but not assigned
            if 'dados' not in session_data:
                session_data['dados'] = {}
            
            session_data['dados']['transferido_humano'] = True
            session_data['dados']['atribuido_para'] = None  # Not assigned to anyone
            
            # Save updated session
            set_session(phone, session_data)
            
            logger.info(f"✅ Conversation {conversation_id} added to global queue")
            return jsonify({'success': True, 'message': 'Conversation added to global queue successfully'})
        else:
            logger.warning(f"⚠️ No session found for conversation {conversation_id}")
            return jsonify({'error': 'No session found for this conversation'}), 404
        
    except Exception as e:
        logger.error(f"❌ Error adding conversation to global queue: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/conversation-actions', methods=['POST'])
@cross_origin()
def conversation_actions():
    """Handle conversation actions: transfer, close, return to queue"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversationId')
        action = data.get('action')  # 'transfer', 'close', 'return'
        target_user_id = data.get('targetUserId')  # for transfer action
        
        if not conversation_id or not action:
            return jsonify({'error': 'conversationId and action are required'}), 400
        
        logger.info(f"🔄 Action {action} on conversation {conversation_id}")
        
        # Here you would implement the logic for each action
        if action == 'transfer':
            if not target_user_id:
                return jsonify({'error': 'targetUserId required for transfer'}), 400
            # Transfer logic
            logger.info(f"Transferring conversation {conversation_id} to user {target_user_id}")
            
        elif action == 'close':
            # Close conversation logic
            logger.info(f"Closing conversation {conversation_id}")
            
        elif action == 'return':
            # Return to queue logic
            logger.info(f"Returning conversation {conversation_id} to queue")
        
        return jsonify({'success': True, 'message': f'Action {action} completed successfully'})
        
    except Exception as e:
        logger.error(f"❌ Error in conversation action: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/conversations/<phone>/sessions', methods=['GET'])
@cross_origin()
def get_conversation_sessions(phone):
    """Get all sessions for a specific phone number"""
    try:
        # Get all messages for this phone number
        all_messages = db.get_messages_by_phone(phone, limit=1000)
        
        if not all_messages:
            return jsonify({'sessions': []})
        
        # Group messages into sessions based on time gaps (30 minutes = new session)
        SESSION_GAP_MINUTES = 30
        sessions = []
        current_session = {
            'id': None,
            'start_time': None,
            'end_time': None,
            'message_count': 0,
            'last_message': None,
            'status': 'active',
            'messages': []
        }
        
        for i, msg in enumerate(all_messages):
            msg_timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
            
            if i == 0:
                # First message starts a session
                current_session['id'] = f"{phone}_{i}"
                current_session['start_time'] = msg['timestamp']
                current_session['end_time'] = msg['timestamp']
                current_session['last_message'] = msg['message_text']
                current_session['messages'].append({
                    'id': msg['id'],
                    'text': msg['message_text'],
                    'direction': msg['direction'],
                    'from': msg['from'],
                    'timestamp': msg['timestamp']
                })
                current_session['message_count'] = 1
            else:
                # Check time gap from previous message
                prev_timestamp = datetime.fromisoformat(all_messages[i-1]['timestamp'].replace('Z', '+00:00'))
                time_diff = (msg_timestamp - prev_timestamp).total_seconds() / 60  # minutes
                
                if time_diff > SESSION_GAP_MINUTES:
                    # Save current session and start new one
                    current_session['status'] = 'finished'
                    sessions.append(current_session)
                    
                    current_session = {
                        'id': f"{phone}_{i}",
                        'start_time': msg['timestamp'],
                        'end_time': msg['timestamp'],
                        'message_count': 1,
                        'last_message': msg['message_text'],
                        'status': 'active',
                        'messages': [{
                            'id': msg['id'],
                            'text': msg['message_text'],
                            'direction': msg['direction'],
                            'from': msg['from'],
                            'timestamp': msg['timestamp']
                        }]
                    }
                else:
                    # Continue current session
                    current_session['end_time'] = msg['timestamp']
                    current_session['last_message'] = msg['message_text']
                    current_session['message_count'] += 1
                    current_session['messages'].append({
                        'id': msg['id'],
                        'text': msg['message_text'],
                        'direction': msg['direction'],
                        'from': msg['from'],
                        'timestamp': msg['timestamp']
                    })
        
        # Add last session
        if current_session['message_count'] > 0:
            # Check if last session is still active (within last 30 minutes)
            last_msg_time = datetime.fromisoformat(current_session['end_time'].replace('Z', '+00:00'))
            now = datetime.now(last_msg_time.tzinfo)
            time_since_last = (now - last_msg_time).total_seconds() / 60
            
            if time_since_last > SESSION_GAP_MINUTES:
                current_session['status'] = 'finished'
            
            sessions.append(current_session)
        
        # Reverse to show most recent first
        sessions.reverse()
        
        # Format response
        formatted_sessions = []
        for session in sessions:
            formatted_sessions.append({
                'id': session['id'],
                'start_time': session['start_time'],
                'end_time': session['end_time'],
                'message_count': session['message_count'],
                'last_message': session['last_message'],
                'status': session['status'],
                'preview': session['last_message'][:100] if session['last_message'] else ''
            })
        
        return jsonify({
            'phone': phone,
            'total_sessions': len(formatted_sessions),
            'sessions': formatted_sessions
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting sessions for {phone}: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/conversations/<phone>/sessions/<session_id>/messages', methods=['GET'])
@cross_origin()
def get_session_messages(phone, session_id):
    """Get all messages for a specific session"""
    try:
        # Get all messages for this phone number
        all_messages = db.get_messages_by_phone(phone, limit=1000)
        
        if not all_messages:
            return jsonify({'messages': []})
        
        # Find the session by extracting index from session_id
        # session_id format: {phone}_{index}
        try:
            session_index = int(session_id.split('_')[-1])
        except:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        # Group messages into sessions (same logic as above)
        SESSION_GAP_MINUTES = 30
        sessions = []
        current_session = {
            'id': None,
            'messages': []
        }
        
        for i, msg in enumerate(all_messages):
            msg_timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
            
            if i == 0:
                current_session['id'] = f"{phone}_{i}"
                current_session['messages'].append({
                    'id': msg['id'],
                    'text': msg['message_text'],
                    'direction': msg['direction'],
                    'from': msg['from'],
                    'timestamp': msg['timestamp']
                })
            else:
                prev_timestamp = datetime.fromisoformat(all_messages[i-1]['timestamp'].replace('Z', '+00:00'))
                time_diff = (msg_timestamp - prev_timestamp).total_seconds() / 60
                
                if time_diff > SESSION_GAP_MINUTES:
                    sessions.append(current_session)
                    current_session = {
                        'id': f"{phone}_{i}",
                        'messages': [{
                            'id': msg['id'],
                            'text': msg['message_text'],
                            'direction': msg['direction'],
                            'from': msg['from'],
                            'timestamp': msg['timestamp']
                        }]
                    }
                else:
                    current_session['messages'].append({
                        'id': msg['id'],
                        'text': msg['message_text'],
                        'direction': msg['direction'],
                        'from': msg['from'],
                        'timestamp': msg['timestamp']
                    })
        
        sessions.append(current_session)
        sessions.reverse()  # Most recent first
        
        # Find the requested session
        target_session = None
        for session in sessions:
            if session['id'] == session_id:
                target_session = session
                break
        
        if not target_session:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'session_id': session_id,
            'phone': phone,
            'message_count': len(target_session['messages']),
            'messages': target_session['messages']
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting session messages: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/upload-media', methods=['POST'])
@cross_origin()
def upload_media():
    """Upload media file and send via WhatsApp"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        phone = request.form.get('phone')
        media_type = request.form.get('type', 'image')
        
        if not phone:
            return jsonify({'error': 'Phone number is required'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file size
        MAX_FILE_SIZES = {
            'image': 10 * 1024 * 1024,  # 10MB
            'document': 50 * 1024 * 1024,  # 50MB
            'audio': 20 * 1024 * 1024,  # 20MB
            'video': 50 * 1024 * 1024  # 50MB
        }
        
        max_size = MAX_FILE_SIZES.get(media_type, 10 * 1024 * 1024)
        if file.content_length and file.content_length > max_size:
            return jsonify({
                'error': f'File too large. Maximum size: {max_size / (1024 * 1024)}MB'
            }), 400
        
        # Read file content
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Generate secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = f"{phone}/{timestamp}_{filename}"
        
        # Upload to Supabase Storage (if configured)
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_KEY", "")
        supabase_bucket = os.getenv("SUPABASE_BUCKET", "media")
        
        media_url = None
        if supabase_url and supabase_key:
            try:
                # Upload to Supabase using REST API
                upload_url = f"{supabase_url}/storage/v1/object/{supabase_bucket}/{file_path}"
                headers = {
                    'apikey': supabase_key,
                    'Authorization': f'Bearer {supabase_key}',
                    'Content-Type': file.content_type or 'application/octet-stream'
                }
                
                upload_response = requests.put(
                    upload_url,
                    data=file_content,
                    headers=headers,
                    timeout=30
                )
                
                if upload_response.status_code in [200, 201]:
                    # Get public URL
                    public_url = f"{supabase_url}/storage/v1/object/public/{supabase_bucket}/{file_path}"
                    media_url = public_url
                    logger.info(f"✅ Arquivo enviado para Supabase: {file_path}")
                else:
                    logger.error(f"❌ Erro ao enviar para Supabase: {upload_response.status_code}")
            except Exception as e:
                logger.error(f"❌ Erro ao fazer upload para Supabase: {e}")
        
        # Send via WhatsApp API (Meta/Venom Bot)
        try:
            # Try Venom Bot first
            venom_response = requests.post(
                'http://localhost:3000/send-media',
                json={
                    'phone': phone,
                    'file': file_path,
                    'type': media_type,
                    'url': media_url,
                    'filename': filename
                },
                files={'file': (filename, file_content, file.content_type)},
                timeout=60
            )
            
            if venom_response.status_code == 200:
                logger.info(f"📤 Mídia enviada via Venom Bot para {phone}")
            else:
                logger.warning(f"⚠️ Venom Bot não respondeu: {venom_response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Venom Bot não disponível: {e}")
        
        # Save message metadata to database
        message_text = f"📎 {filename}"
        if media_url:
            message_text += f" ({media_url})"
        
        timestamp = datetime.now().isoformat()
        db.save_message(
            phone_number=phone,
            message_text=message_text,
            direction='sent',
            from_field='agent',
            timestamp=timestamp
        )
        
        # Emit WebSocket update
        emit_message_update()
        
        return jsonify({
            'success': True,
            'message': 'Media uploaded and sent successfully',
            'url': media_url,
            'file_path': file_path
        })
        
    except Exception as e:
        logger.error(f"❌ Error uploading media: {e}")
        return jsonify({'error': str(e)}), 500
