"""
Tests pour l'agent LangChain IMT.
"""
import sys
from pathlib import Path
import os
from unittest.mock import patch, MagicMock, Mock
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.langchain_agent import create_imt_agent, run_agent
from app.langchain_tools import tools, get_tool_names


# ===========================
# Tests des LangChain Tools
# ===========================

class TestLangChainTools:
    """Tests pour les LangChain Tools."""
    
    def test_tools_list_exists(self):
        """Test que la liste des outils existe."""
        assert tools is not None
        assert isinstance(tools, list)
        assert len(tools) == 2
    
    def test_tool_names(self):
        """Test que les noms des outils sont corrects."""
        names = get_tool_names()
        assert "search_imt" in names
        assert "send_email" in names
    
    def test_search_imt_tool_exists(self):
        """Test que l'outil search_imt existe."""
        tool = next((t for t in tools if t.name == "search_imt"), None)
        assert tool is not None
        assert tool.description is not None
    
    def test_send_email_tool_exists(self):
        """Test que l'outil send_email existe."""
        tool = next((t for t in tools if t.name == "send_email"), None)
        assert tool is not None
        assert tool.description is not None
    
    def test_search_imt_tool_callable(self):
        """Test que l'outil search_imt peut être appelé."""
        from app.langchain_tools import search_imt
        result = search_imt.invoke({"query": "formations"})
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_send_email_tool_callable(self):
        """Test que l'outil send_email peut être appelé (mode simulation)."""
        from app.langchain_tools import send_email
        with patch.dict(os.environ, {}, clear=True):
            result = send_email.invoke({
                "subject": "Test",
                "content": "Test content"
            })
            assert isinstance(result, str)
            assert "simulation" in result.lower()


# ===========================
# Tests de création d'agent
# ===========================

class TestAgentCreation:
    """Tests pour la création de l'agent LangChain."""
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'fake_key_for_testing'})
    def test_create_agent_with_api_key(self):
        """Test de création d'agent avec clé API."""
        agent = create_imt_agent(verbose=False)
        assert agent is not None
        assert hasattr(agent, 'invoke')
    
    def test_create_agent_without_api_key(self):
        """Test de création d'agent sans clé API."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY"):
                create_imt_agent()
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'fake_key'})
    def test_create_agent_with_custom_temperature(self):
        """Test de création avec température personnalisée."""
        agent = create_imt_agent(temperature=0.5, verbose=False)
        assert agent is not None
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'fake_key'})
    def test_create_agent_with_custom_iterations(self):
        """Test de création avec nombre d'itérations personnalisé."""
        agent = create_imt_agent(max_iterations=10, verbose=False)
        assert agent is not None


# ===========================
# Tests d'exécution d'agent
# ===========================

class TestAgentExecution:
    """Tests pour l'exécution de l'agent."""
    
    def test_run_agent_with_empty_question(self):
        """Test avec question vide."""
        result = run_agent("")
        assert "valide" in result.lower()
    
    def test_run_agent_without_api_key(self):
        """Test d'exécution sans clé API."""
        with patch.dict(os.environ, {}, clear=True):
            result = run_agent("test question")
            assert "GEMINI_API_KEY" in result or "initialisé" in result
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'fake_key'})
    @patch('app.langchain_agent.AgentExecutor')
    def test_run_agent_with_mock_executor(self, mock_executor_class):
        """Test d'exécution avec mock d'executor."""
        # Créer un mock d'agent
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {"output": "Réponse test"}
        
        result = run_agent("test question", agent=mock_agent)
        
        assert isinstance(result, str)
        assert len(result) > 0
        mock_agent.invoke.assert_called_once()
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'fake_key'})
    def test_run_agent_handles_exception(self):
        """Test de gestion d'erreur lors de l'exécution."""
        # Créer un mock qui lève une exception
        mock_agent = MagicMock()
        mock_agent.invoke.side_effect = Exception("Test error")
        
        result = run_agent("test question", agent=mock_agent)
        
        assert "erreur" in result.lower()
        assert "Test error" in result


# ===========================
# Tests d'intégration
# ===========================

class TestLangChainIntegration:
    """Tests d'intégration pour l'agent LangChain."""
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'fake_key'})
    @patch('app.langchain_agent.ChatGoogleGenerativeAI')
    def test_agent_with_search_query(self, mock_llm_class):
        """Test d'agent avec requête de recherche."""
        # Mock du LLM pour retourner une décision de recherche
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        
        # Créer l'agent (avec le LLM mocké)
        agent = create_imt_agent(verbose=False)
        
        # Le test vérifie juste que l'agent peut être créé
        assert agent is not None
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'fake_key'})
    def test_tools_are_registered(self):
        """Test que les outils sont enregistrés dans l'agent."""
        agent = create_imt_agent(verbose=False)
        
        # Vérifier que l'agent a accès aux outils
        assert hasattr(agent, 'tools')
        assert len(agent.tools) == 2


# ===========================
# Tests de compatibilité
# ===========================

class TestBackwardCompatibility:
    """Tests de compatibilité avec l'ancien agent."""
    
    def test_old_agent_still_works(self):
        """Test que l'ancien agent fonctionne toujours."""
        from app.agent import agent as old_agent
        
        # L'ancien agent devrait toujours fonctionner
        result = old_agent("test question")
        assert isinstance(result, str)
    
    def test_both_agents_importable(self):
        """Test que les deux agents peuvent être importés."""
        from app.agent import agent as old_agent
        from app.langchain_agent import run_agent as new_agent
        
        assert old_agent is not None
        assert new_agent is not None
