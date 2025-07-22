from flask import Blueprint, jsonify, request
from session_store import get_all_sessions
from database import db
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

@stats_bp.route("/reports", methods=["GET"])
def get_reports():
    """Get comprehensive reporting data"""
    try:
        # Get query parameters
        period = request.args.get('period', '24h')
        filter_type = request.args.get('filter', 'all')
        agent = request.args.get('agent', 'all')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Build filters
        filters = {
            'type': filter_type,
            'agent': agent,
            'start_date': start_date,
            'end_date': end_date
        }
        
        # Get reporting data from database
        report_data = db.get_reporting_data(period, filters)
        
        return jsonify({
            'success': True,
            'data': report_data,
            'filters': {
                'period': period,
                'filter_type': filter_type,
                'agent': agent,
                'start_date': start_date,
                'end_date': end_date
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@stats_bp.route("/reports/export", methods=["POST"])
def export_reports():
    """Export reports in different formats"""
    try:
        data = request.get_json()
        format_type = data.get('format', 'csv')
        period = data.get('period', '24h')
        filters = data.get('filters', {})
        
        # Get data for export
        report_data = db.get_reporting_data(period, filters)
        
        if format_type == 'csv':
            # Generate CSV content
            csv_content = generate_csv_export(report_data)
            return jsonify({
                'success': True,
                'format': 'csv',
                'filename': f'report_{period}_{datetime.now().strftime("%Y%m%d")}.csv',
                'content': csv_content
            })
        elif format_type == 'excel':
            # For Excel, we'd need a library like xlsx
            return jsonify({
                'success': True,
                'format': 'excel',
                'filename': f'report_{period}_{datetime.now().strftime("%Y%m%d")}.xlsx',
                'message': 'Excel export would be implemented with xlsx library'
            })
        elif format_type == 'pdf':
            # For PDF, we'd need a library like jsPDF
            return jsonify({
                'success': True,
                'format': 'pdf',
                'filename': f'report_{period}_{datetime.now().strftime("%Y%m%d")}.pdf',
                'message': 'PDF export would be implemented with jsPDF library'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported format'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_csv_export(report_data):
    """Generate CSV content from report data"""
    lines = []
    
    # Header
    lines.append("Relatório de Conversas")
    lines.append("")
    
    # Metrics
    lines.append("Métricas Gerais")
    lines.append("Conversas Totais,Conversas Ativas,Conversas Encerradas,Transferidas")
    conv = report_data['conversations']
    lines.append(f"{conv['total']},{conv['active']},{conv['closed']},{conv['transferred']}")
    lines.append("")
    
    # Messages
    lines.append("Mensagens")
    lines.append("Total,Recebidas,Enviadas,Tempo Médio de Resposta")
    msg = report_data['messages']
    lines.append(f"{msg['total']},{msg['received']},{msg['sent']},{msg['avgResponseTime']}")
    lines.append("")
    
    # Agents Performance
    lines.append("Performance dos Agentes")
    lines.append("Nome,Conversas,Tempo Médio,Satisfação")
    for agent in report_data['agents']['performance']:
        lines.append(f"{agent['name']},{agent['conversations']},{agent['avgTime']},{agent['satisfaction']}")
    lines.append("")
    
    # Daily Trends
    lines.append("Tendências Diárias")
    lines.append("Data,Conversas,Mensagens")
    for day in report_data['trends']['daily']:
        lines.append(f"{day['date']},{day['conversations']},{day['messages']}")
    
    return "\n".join(lines)
