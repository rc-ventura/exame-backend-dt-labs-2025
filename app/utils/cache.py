import redis.asyncio as redis  # Usando o módulo async do redis-py
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from typing import Optional
import json

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter a URL do Redis do arquivo .env
REDIS_URL = os.getenv("REDIS_URL")  # URL padrão se não encontrar a variável

# Verificar se a URL foi carregada corretamente
if not REDIS_URL:
    raise ValueError("REDIS_URL environment variable is not set")

# Função para criar a conexão Redis assíncrona
async def get_redis_connection():
    try:
        return await redis.from_url(REDIS_URL)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Redis: {str(e)}")

# Função para armazenar um valor no cache
async def set_cache_key(key: str, value: str, expire: int = 3600):
    redis_conn = await get_redis_connection()
    
    # Serializa a lista em uma string JSON antes de armazenar no Redis
    value = json.dumps(value)  # Converte a lista para string JSON
    await redis_conn.setex(key, expire, value)  # Armazena o valor com tempo de expiração
    await redis_conn.close()

# Função para pegar um valor do cache
async def get_cache_key(key: str) -> Optional[str]:
    redis_conn = await get_redis_connection()
    value = await redis_conn.get(key)
    await redis_conn.close()
    return value.decode('utf-8') if value else None
