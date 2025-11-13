from flask import Blueprint, request, jsonify, Response, stream_with_context
from flask_cors import cross_origin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import logging
import os
from dotenv import load_dotenv
from typing import Optional
import time

load_dotenv()

logger = logging.getLogger(__name__)

media_bp = Blueprint("media", __name__)

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "media")

# Criar sessão reutilizável com connection pooling
_session = None

def get_session():
    """Retorna uma sessão HTTP reutilizável com connection pooling otimizado"""
    global _session
    
    if _session is None:
        _session = requests.Session()
        
        # Configurar retry strategy para erros temporários
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        
        # Configurar HTTPAdapter com pool de conexões
        adapter = HTTPAdapter(
            pool_connections=10,  # Número de pools de conexão
            pool_maxsize=20,       # Máximo de conexões por pool
            max_retries=retry_strategy,
            pool_block=False
        )
        
        _session.mount("http://", adapter)
        _session.mount("https://", adapter)
        
        # Headers padrão para melhor performance
        _session.headers.update({
            'User-Agent': 'WhatsApp-Bot/1.0',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        logger.info("✅ Sessão HTTP criada com connection pooling otimizado")
    
    return _session

def download_media_from_supabase(file_path: str, chunk_size: int = 256 * 1024) -> Optional[Response]:
    """
    Faz download otimizado de mídia do Supabase usando streaming
    
    Args:
        file_path: Caminho do arquivo no bucket do Supabase
        chunk_size: Tamanho do chunk para streaming (256KB por padrão)
    
    Returns:
        Response do Flask com streaming ou None em caso de erro
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("❌ SUPABASE_URL ou SUPABASE_KEY não configurados")
        return None
    
    try:
        session = get_session()
        
        # Construir URL do arquivo no Supabase Storage
        file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_path}"
        
        logger.info(f"📥 Iniciando download de {file_path} do Supabase")
        start_time = time.time()
        
        # Fazer requisição com stream=True para download em chunks
        response = session.get(
            file_url,
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
            },
            stream=True,
            timeout=(10, 30)  # (connect timeout, read timeout)
        )
        
        response.raise_for_status()
        
        # Determinar content type
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        
        # Função geradora para streaming
        def generate():
            try:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        yield chunk
            finally:
                response.close()
        
        download_time = time.time() - start_time
        logger.info(f"✅ Download concluído em {download_time:.2f}s")
        
        return Response(
            stream_with_context(generate()),
            content_type=content_type,
            headers={
                'Content-Disposition': f'inline; filename="{os.path.basename(file_path)}"',
                'Cache-Control': 'public, max-age=3600',
                'X-Download-Time': f'{download_time:.2f}s'
            }
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro ao fazer download do Supabase: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro inesperado no download: {e}")
        return None

@media_bp.route("/media/<path:file_path>", methods=["GET"])
@cross_origin()
def get_media(file_path: str):
    """
    Endpoint para servir mídia do Supabase com otimizações
    
    Args:
        file_path: Caminho do arquivo no bucket (ex: 'images/photo.jpg')
    """
    try:
        response = download_media_from_supabase(file_path)
        
        if response is None:
            return jsonify({'error': 'Erro ao fazer download da mídia'}), 500
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint de mídia: {e}")
        return jsonify({'error': str(e)}), 500

@media_bp.route("/media/health", methods=["GET"])
@cross_origin()
def health_check():
    """Endpoint de health check para verificar configuração do Supabase"""
    return jsonify({
        'status': 'ok',
        'supabase_configured': bool(SUPABASE_URL and SUPABASE_KEY),
        'bucket': SUPABASE_BUCKET,
        'connection_pooling': True
    }), 200
