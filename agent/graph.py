"""
agent/graph.py
--------------
Define el grafo del agente — cómo se conectan los nodos.

Por qué LangGraph y no una función secuencial simple:
    Una función secuencial simple haría lo mismo para este flujo lineal,
    pero LangGraph nos da:
    - Estado tipado y trazable en cada paso
    - Fácil de extender con nodos condicionales (ej: si score > 0.9
      saltar directo a rechazo sin dictamen)
    - Compatible con LangSmith para observabilidad en producción
    - El grafo es serializable — puedes pausar y reanudar

Flujo:
    START → extractor → scorer → dictator → END
"""

from langgraph.graph import StateGraph, START, END
from agent.state import ClaimState
from agent.nodes.extractor import extractor_node
from agent.nodes.scorer import scorer_node
from agent.nodes.dictator import dictator_node


def build_graph():
    """
    Construye y compila el grafo del agente.

    Returns:
        CompiledGraph: grafo listo para invocar
    """
    # Inicializar el grafo con el estado tipado
    graph = StateGraph(ClaimState)

    # Registrar nodos
    graph.add_node("extractor", extractor_node)
    graph.add_node("scorer", scorer_node)
    graph.add_node("dictator", dictator_node)

    # Definir flujo
    graph.add_edge(START, "extractor")
    graph.add_edge("extractor", "scorer")
    graph.add_edge("scorer", "dictator")
    graph.add_edge("dictator", END)

    return graph.compile()


# Instancia global del grafo — se compila una sola vez
fraud_agent = build_graph()


def analyze_claim(documento_texto: str) -> dict:
    """
    Punto de entrada principal del agente.
    Recibe texto del siniestro y retorna el análisis completo.

    Args:
        documento_texto: texto del siniestro en cualquier formato

    Returns:
        dict con entidades, fraud_result y dictamen
    """
    initial_state = ClaimState(
        documento_texto=documento_texto,
        entidades=None,
        fraud_result=None,
        dictamen=None,
        error=None,
    )

    result = fraud_agent.invoke(initial_state)

    return {
        "entidades": result.get("entidades"),
        "fraud_result": result.get("fraud_result"),
        "dictamen": result.get("dictamen"),
        "error": result.get("error"),
    }