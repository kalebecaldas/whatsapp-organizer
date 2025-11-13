from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime, timezone
import json
import time

from api.routes import api_bp, init_socketio
from api.stats_routes import stats_bp
from api.media_routes import media_bp
from api.meta_routes import meta_bp
from api.internal_conversations_routes import internal_bp, init_internal_socketio
from session_store import redis_client
from message_store import messages_store
from database import db
from handlers.message_handler import handle_message

# Carregar variáveis de ambiente
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY não definida. Verifique o arquivo .env.")

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    print("⚠️ REDIS_URL não definida no .env. Usando padrão: redis://localhost:6379/0")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# Inicializa o app Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Configurar CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configurar SocketIO
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='threading',
    logger=True,
    engineio_logger=True
)

# Initialize socketio for internal conversations
init_internal_socketio(socketio)

# Blueprints
app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(stats_bp, url_prefix="/api")
app.register_blueprint(media_bp, url_prefix="/api")
app.register_blueprint(meta_bp, url_prefix="/api/meta")
app.register_blueprint(internal_bp, url_prefix="/api")

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'SQLite'
    }), 200

# Endpoint principal do webhook
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    """Webhook endpoint for WhatsApp messages"""
    if request.method == 'GET':
        return "Webhook ativo com Venom Bot", 200

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Requisição inválida"}), 400

        from_number = data.get("from", "")
        incoming_msg = data.get("body", "").strip()
        
        logger.info(f"🔔 Mensagem recebida de {from_number}: {incoming_msg}")

        # PRIMEIRO: Salvar mensagem do usuário imediatamente e emitir WebSocket
        user_timestamp = datetime.now(timezone.utc).isoformat()
        db.save_message(
            phone_number=from_number,
            message_text=incoming_msg,
            direction='received',
            from_field='user',
            timestamp=user_timestamp
        )
        
        # Emitir WebSocket imediatamente para mostrar a mensagem do usuário
        logger.info("🔔 Emitindo mensagem do usuário via WebSocket...")
        emit_message_update()
        logger.info("✅ Mensagem do usuário emitida via WebSocket")

        # SEGUNDO: Processar resposta do bot (pode demorar)
        reply_text = handle_message(from_number, incoming_msg) or "Desculpe, não entendi."
        logger.info(f"💬 Resposta gerada: {reply_text}")

        # TERCEIRO: Salvar resposta do bot e emitir WebSocket novamente
        if reply_text:
            bot_timestamp = datetime.now(timezone.utc).isoformat()
            db.save_message(
                phone_number=from_number,
                message_text=reply_text,
                direction='sent',
                from_field='agent',
                timestamp=bot_timestamp
            )
            
            # Emitir WebSocket novamente para mostrar a resposta do bot
            logger.info("🔔 Emitindo resposta do bot via WebSocket...")
            emit_message_update()
            logger.info("✅ Resposta do bot emitida via WebSocket")

        return jsonify({"result": reply_text, "status": "ok"}), 200
        
    except Exception as e:
        logger.error(f"❌ Error in webhook: {e}")
        return jsonify({"error": str(e)}), 500

# Eventos do WebSocket
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info("🔌 Cliente conectado via WebSocket")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info("🔌 Cliente desconectado via WebSocket")

@socketio.on('join_conversation')
def handle_join_conversation(data):
    conversation_id = data.get('conversation_id')
    if conversation_id:
        socketio.emit('user_joined', {
            'conversation_id': conversation_id,
            'message': f'Usuário entrou na conversa {conversation_id}'
        })

# Função para emitir atualizações de mensagens
def emit_message_update():
    """Emit message update to all connected clients"""
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
        socketio.emit('message_update', {'conversations': conversations_list})
        logger.info("✅ Evento 'message_update' emitido via WebSocket")
        
    except Exception as e:
        logger.error(f"❌ Error emitting message update: {e}")

# Função para emitir atualizações de estatísticas
def emit_stats_update(stats_data):
    """Emite atualização de estatísticas para todos os clientes conectados"""
    socketio.emit('stats_update', stats_data)

# Executa o servidor localmente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 Iniciando servidor na porta {port}")
    
    # Configurar Redis URL
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    print(f"⚠️ REDIS_URL não definida no .env. Usando padrão: {redis_url}")
    
    # Migrar mensagens antigas na inicialização
    if messages_store:
        print("🔄 Migrando mensagens antigas na inicialização...")
        db.migrate_old_messages(messages_store)
        messages_store.clear()
        print("✅ Migração concluída")
    
    # Iniciar servidor com SocketIO
    socketio.run(app, host="0.0.0.0", port=port, debug=True, allow_unsafe_werkzeug=True)
