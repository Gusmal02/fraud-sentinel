"""
agent/state.py
--------------
Define el estado compartido del agente.

Por qué un State separado:
    Todos los nodos leen y escriben en el mismo State.
    Tenerlo en un archivo separado evita imports circulares
    y hace explícito qué información fluye por el sistema.
"""

from typing import TypedDict, Optional


class ClaimState(TypedDict):
    """
    Estado compartido del agente durante el análisis de un siniestro.
    
    Cada campo es llenado por un nodo diferente:
        - documento_texto: llenado por el input inicial
        - entidades:       llenado por el nodo extractor
        - fraud_result:    llenado por el nodo scorer
        - dictamen:        llenado por el nodo dictator
        - error:           llenado por cualquier nodo si algo falla
    """
    documento_texto: str           # Texto del siniestro en Markdown
    entidades: Optional[dict]      # Entidades extraídas por el LLM
    fraud_result: Optional[dict]   # Resultado del clasificador
    dictamen: Optional[str]        # Dictamen final en lenguaje natural
    error: Optional[str]           # Error si algo falla en el proceso