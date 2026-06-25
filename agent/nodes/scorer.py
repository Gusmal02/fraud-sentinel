"""
agent/nodes/scorer.py
----------------------
Nodo 2 del agente: toma las entidades extraídas y genera el score de fraude.

Por qué este nodo es simple:
    La lógica de scoring ya está en classifier/predict.py.
    Este nodo solo hace el puente entre el estado del agente
    y el clasificador. Un nodo con una sola responsabilidad
    es más fácil de testear y mantener.

Por qué verificamos el error antes de ejecutar:
    Si el extractor falló, no tiene sentido intentar el scoring.
    El agente detecta esto y salta directo al dictamen de error.
"""

from agent.state import ClaimState
from classifier.predict import predict_fraud


def scorer_node(state: ClaimState) -> ClaimState:
    """
    Llama al clasificador LightGBM con las entidades extraídas.

    Args:
        state: estado actual con entidades

    Returns:
        state actualizado con fraud_result o error
    """
    # Si ya hay un error previo, no continuamos
    if state.get("error"):
        print(f"⚠️  Scorer: saltando por error previo")
        return state

    if not state.get("entidades"):
        error_msg = "Scorer: no hay entidades para clasificar"
        print(f"❌ {error_msg}")
        return {**state, "error": error_msg}

    try:
        fraud_result = predict_fraud(state["entidades"])

        print(f"✅ Scorer: score={fraud_result['fraud_score']} "
              f"nivel={fraud_result['risk_level']}")

        return {**state, "fraud_result": fraud_result}

    except Exception as e:
        error_msg = f"Scorer falló: {e}"
        print(f"❌ {error_msg}")
        return {**state, "error": error_msg}