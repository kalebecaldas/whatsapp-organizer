from flask import Blueprint, jsonify
from session_store import get_all_sessions
from datetime import datetime, timedelta
import json

stats_bp = Blueprint('stats', __name__)

@stats_bp.route("/sessions", methods=["GET"])
def get_stats():
    agora = datetime.utcnow()
    limite = agora - timedelta(hours=8)

    total_usuarios = 0

    for user_id, session_data in get_all_sessions().items():
        if isinstance(session_data, dict):
            historico = session_data.get("historico", [])
            # Conta usuários que têm histórico de mensagens (considerados ativos)
            if historico and len(historico) > 0:
                total_usuarios += 1

    return jsonify({"usuarios_ativos_ultimas_8h": total_usuarios})
