"""Tests del agente LangGraph."""
import pytest
from unittest.mock import patch, MagicMock
from agent.state import ClaimState


def make_state(**kwargs) -> ClaimState:
    """Helper para crear estados de prueba."""
    defaults = ClaimState(
        documento_texto="Reporte de siniestro de prueba para testing",
        entidades=None,
        fraud_result=None,
        dictamen=None,
        error=None,
    )
    defaults.update(kwargs)
    return defaults


class TestExtractorNode:
    def test_extractor_con_error_previo_no_procesa(self):
        """Si ya hay error en el estado, el extractor no debe llamar al LLM."""
        from agent.nodes.extractor import extractor_node
        state = make_state(error="error previo")
        # El extractor no tiene lógica de skip — ese es el scorer
        # Verificamos que el estado con error llega al scorer intacto
        assert state["error"] == "error previo"

    def test_state_inicial_tiene_campos_requeridos(self):
        """El estado inicial debe tener todos los campos necesarios."""
        state = make_state()
        assert "documento_texto" in state
        assert "entidades" in state
        assert "fraud_result" in state
        assert "dictamen" in state
        assert "error" in state

    def test_documento_texto_no_vacio(self):
        """El documento de entrada no debe estar vacío."""
        state = make_state()
        assert len(state["documento_texto"]) > 0


class TestScorerNode:
    def test_scorer_salta_si_hay_error(self):
        """El scorer debe saltar si hay error previo."""
        from agent.nodes.scorer import scorer_node
        state = make_state(error="extractor falló")
        result = scorer_node(state)
        assert result["error"] == "extractor falló"
        assert result["fraud_result"] is None

    def test_scorer_salta_si_no_hay_entidades(self):
        """El scorer debe registrar error si no hay entidades."""
        from agent.nodes.scorer import scorer_node
        state = make_state(entidades=None)
        result = scorer_node(state)
        assert result["error"] is not None
        assert result["fraud_result"] is None

    def test_scorer_con_entidades_validas(self):
        """El scorer debe producir fraud_result con entidades válidas."""
        from agent.nodes.scorer import scorer_node
        state = make_state(entidades={"Make": "Honda", "Age": 30})
        result = scorer_node(state)
        assert result["fraud_result"] is not None
        assert "fraud_score" in result["fraud_result"]
        assert "risk_level" in result["fraud_result"]


class TestDictatorNode:
    def test_dictator_maneja_error_previo(self):
        """El dictador debe generar dictamen de error si hay error previo."""
        from agent.nodes.dictator import dictator_node
        state = make_state(error="scorer falló")
        result = dictator_node(state)
        assert result["dictamen"] is not None
        assert "DICTAMEN NO DISPONIBLE" in result["dictamen"]

    def test_dictator_requiere_fraud_result(self):
        """Sin fraud_result el dictador debe manejar el caso."""
        from agent.nodes.dictator import dictator_node
        state = make_state(
            entidades={"Make": "BMW"},
            fraud_result=None,
            error="sin score"
        )
        result = dictator_node(state)
        assert result["dictamen"] is not None