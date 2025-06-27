import redis
import json
import os
from typing import Dict, Any, Optional
from collections.abc import Iterable

# Define prefixos para organizar as chaves no Redis
SESSION_PREFIX = "sessao_user:"
LOCK_PREFIX = "lock:sessao_user:" 

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# Define a duração da sessão (8 horas) e da trava (25 segundos)
SESSION_TTL_SECONDS = 8 * 60 * 60
LOCK_TTL_SECONDS = 25

def get_session(user_id: str) -> Dict[str, Any]:
    """Retorna a sessão do usuário do Redis com uma estrutura padrão segura."""
    try:
        raw = redis_client.get(SESSION_PREFIX + user_id)
        if raw and isinstance(raw, str):
            data = json.loads(raw)
            if isinstance(data, dict):
                # Garante que a estrutura mínima da sessão sempre exista
                data.setdefault("etapa", "inicio")
                data.setdefault("dados", {})
                data.setdefault("historico", [])
                return data
    except Exception as e:
        print(f"❌ Erro ao ler sessão de {user_id}: {e}")
    
    # Retorna uma sessão nova e limpa se não existir ou se ocorrer um erro
    return { "etapa": "inicio", "dados": {}, "historico": [] }

def set_session(user_id: str, session_data: Dict[str, Any]) -> None:
    """Salva ou atualiza a sessão do usuário no Redis com TTL."""
    try:
        session_string = json.dumps(session_data, indent=2)
        redis_client.set(SESSION_PREFIX + user_id, session_string, ex=SESSION_TTL_SECONDS)
        print(f"✅ Sessão salva no Redis para {user_id} - etapa: {session_data.get('etapa')}")
    except Exception as e:
        print(f"❌ Erro ao salvar sessão de {user_id}: {e}")

def acquire_lock(user_id: str) -> bool:
    """Tenta adquirir uma trava para um usuário, impedindo processamento concorrente."""
    lock_key = LOCK_PREFIX + user_id
    try:
        # 'nx=True' garante que a chave só é definida se ela NÃO existir (operação atômica).
        lock_adquirido = redis_client.set(lock_key, "locked", ex=LOCK_TTL_SECONDS, nx=True)
        return bool(lock_adquirido)
    except Exception as e:
        print(f"❌ Erro ao tentar adquirir a trava para {user_id}: {e}")
        return False

def release_lock(user_id: str) -> None:
    """Libera a trava de um usuário após o processamento da mensagem."""
    lock_key = LOCK_PREFIX + user_id
    try:
        redis_client.delete(lock_key)
    except Exception as e:
        print(f"❌ Erro ao tentar liberar a trava para {user_id}: {e}")

def get_all_sessions() -> Dict[str, Dict[str, Any]]:
    """Retorna todas as sessões ativas no Redis (para estatísticas)."""
    try:
        pattern = SESSION_PREFIX + "*"
        raw_keys = redis_client.keys(pattern)
        if isinstance(raw_keys, Iterable) and not isinstance(raw_keys, str):
            key_list = list(raw_keys)
        else:
            key_list = []
        
        if not key_list:
            print("📊 Nenhuma sessão encontrada no Redis")
            return {}
            
        result: Dict[str, Dict[str, Any]] = {}
        values = redis_client.mget(key_list)
        
        if isinstance(values, list):
            for i, key in enumerate(key_list):
                value = values[i]
                if value and isinstance(value, str):
                    user_id = key.replace(SESSION_PREFIX, "")
                    try:
                        session = json.loads(value)
                        if isinstance(session, dict):
                            # Garante que a estrutura mínima da sessão sempre exista
                            session.setdefault("etapa", "inicio")
                            session.setdefault("dados", {})
                            session.setdefault("historico", [])
                            result[user_id] = session
                        else:
                            print(f"⚠️ Sessão inválida para {user_id}: não é um dicionário")
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Sessão corrompida para {user_id}: {e}")
                    except Exception as e:
                        print(f"❌ Erro ao processar sessão de {user_id}: {e}")
        
        print(f"📊 {len(result)} sessões válidas encontradas")
        return result
    except Exception as e:
        print(f"❌ Erro ao buscar sessões: {e}")
        return {}

