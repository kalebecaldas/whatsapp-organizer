import redis
import os
import json


# Redis config — ajuste se necessário
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def get_session(key: str):
    session = redis_client.get(f"sessao:{key}")
    return session if session else {}

def set_session(key: str, value: dict):
    redis_client.set(f"sessao:{key}", json.dumps(value), ex=60 * 60 * 8)  # expira em 8h
