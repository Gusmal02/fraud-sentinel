"""
api/cache.py
-------------
Caché Redis para resultados del agente.

Por qué cachear el resultado completo y no solo el score:
    El dictamen incluye contexto RAG que puede variar.
    Cacheamos el resultado completo para garantizar consistencia
    entre la primera y segunda llamada con el mismo documento.

Por qué TTL de 24 horas:
    Los siniestros no cambian en el día. Si llega el mismo
    reporte dos veces en 24 horas, el resultado es el mismo.
    Después de 24 horas forzamos re-análisis por si hay
    nuevos patrones en ChromaDB.

Por qué hash MD5 como clave:
    El texto del siniestro puede ser muy largo.
    MD5 produce una clave corta y única de 32 caracteres.
    No usamos MD5 para seguridad aquí — solo para identificación.
"""

import redis
import hashlib
import json
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", 86400))  # 24 horas


def get_redis_client() -> Optional[redis.Redis]:
    """
    Retorna cliente Redis o None si no está disponible.

    Por qué retornar None en lugar de lanzar excepción:
        Redis es una optimización, no un requisito crítico.
        Si Redis no está disponible, el sistema funciona igual
        pero sin caché — degradación elegante.
    """
    try:
        client = redis.from_url(REDIS_URL, decode_responses=True)
        client.ping()
        return client
    except Exception:
        return None


def make_cache_key(texto: str) -> str:
    """
    Genera clave de caché basada en hash MD5 del texto.

    Args:
        texto: texto del siniestro

    Returns:
        str: clave en formato 'fraud_sentinel:md5hash'
    """
    hash_md5 = hashlib.md5(texto.encode(), usedforsecurity=False).hexdigest()
    return f"fraud_sentinel:{hash_md5}"


def get_cached_result(texto: str) -> Optional[dict]:
    """
    Busca resultado en caché.

    Args:
        texto: texto del siniestro

    Returns:
        dict con resultado previo o None si no está en caché
    """
    client = get_redis_client()
    if not client:
        return None

    try:
        key = make_cache_key(texto)
        cached = client.get(key)
        if cached:
            print(f"✅ Cache HIT — {key[:40]}...")
            return json.loads(cached)
        print(f"❌ Cache MISS — {key[:40]}...")
        return None
    except Exception:
        return None


def set_cached_result(texto: str, result: dict) -> bool:
    """
    Guarda resultado en caché con TTL.

    Args:
        texto: texto del siniestro
        result: resultado del agente a cachear

    Returns:
        bool: True si se guardó correctamente
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        key = make_cache_key(texto)
        client.setex(key, CACHE_TTL, json.dumps(result, ensure_ascii=False))
        print(f"✅ Cache SET — TTL {CACHE_TTL}s")
        return True
    except Exception:
        return False