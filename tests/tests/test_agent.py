import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agent import agent, _call_gemini, reformulate_answer


class TestAgent:
    """Tests pour la fonction principale agent()"""
    
    def test_agent_with_search_query(self):
        """Test agent avec une question de recherche normale"""
        result = agent("Quelles sont les formations disponibles ?")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_agent_with_email_query(self):
        """Test agent avec une demande d'envoi d'email"""
        result = agent("Je veux contacter le directeur")
        assert isinstance(result, str)
        assert "email" in result.lower() or "envoyé" in result.lower() or "simulation" in result.lower()
    
    def test_agent_with_empty_question(self):
        """Test agent avec question vide"""
        result = agent("")
        assert "reformuler" in result.lower() or "compris" in result.lower()
    
    def test_agent_with_whitespace_only(self):
        """Test agent avec seulement des espaces"""
        result = agent("   ")
        assert "reformuler" in result.lower() or "compris" in result.lower()
    
    @patch('app.agent.GENAI_AVAILABLE', False)
    def test_agent_fallback_without_gemini(self):
        """Test agent utilise le fallback heuristique sans Gemini"""
        # Test recherche
        result = agent("Où est l'IMT ?")
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Test email
        result_email = agent("Envoyer un email au directeur")
        assert isinstance(result_email, str)
        assert "email" in result_email.lower() or "simulation" in result_email.lower()
    
    @patch('app.agent._call_gemini')
    def test_agent_with_gemini_search_decision(self, mock_gemini):
        """Test agent quand Gemini décide SEARCH"""
        mock_gemini.return_value = "SEARCH"
        result = agent("Quelles formations ?")
        assert isinstance(result, str)
        mock_gemini.assert_called()
    
    @patch('app.agent._call_gemini')
    def test_agent_with_gemini_email_decision(self, mock_gemini):
        """Test agent quand Gemini décide EMAIL"""
        mock_gemini.return_value = "EMAIL"
        result = agent("Contactez l'IMT")
        assert isinstance(result, str)
        assert "email" in result.lower() or "envoyé" in result.lower() or "simulation" in result.lower()
        mock_gemini.assert_called()
    
    @patch('app.agent.search_imt')
    @patch('app.agent._call_gemini')
    def test_agent_handles_search_tool_error(self, mock_gemini, mock_search):
        """Test agent gère les erreurs de l'outil de recherche"""
        mock_gemini.return_value = "SEARCH"
        mock_search.side_effect = Exception("Erreur recherche")
        result = agent("Test question")
        assert isinstance(result, str)
        # L'agent doit retourner un message d'erreur propre
        assert "erreur" in result.lower() or "réessayer" in result.lower()
    
    def test_agent_with_location_keywords(self):
        """Test heuristique avec mots-clés de localisation"""
        result = agent("Où se trouve l'IMT")
        assert isinstance(result, str)
        assert len(result) > 10  # Doit avoir une vraie réponse
    
    def test_agent_with_director_keywords(self):
        """Test heuristique avec mot-clé 'directeur'"""
        result = agent("Je veux écrire au directeur")
        assert isinstance(result, str)
        # Doit déclencher l'action EMAIL
        assert "email" in result.lower() or "simulation" in result.lower()


class TestCallGemini:
    """Tests pour la fonction _call_gemini()"""
    
    @patch('app.agent.GENAI_AVAILABLE', False)
    def test_call_gemini_when_unavailable(self):
        """Test _call_gemini retourne None quand Gemini indisponible"""
        result = _call_gemini("test prompt")
        assert result is None
    
    @patch('app.agent.GENAI_AVAILABLE', True)
    @patch('app.agent.genai.GenerativeModel')
    def test_call_gemini_success(self, mock_model):
        """Test _call_gemini avec réponse réussie"""
        mock_response = MagicMock()
        mock_response.text = "SEARCH"
        mock_model.return_value.generate_content.return_value = mock_response
        
        result = _call_gemini("test prompt")
        assert result == "SEARCH"
    
    @patch('app.agent.GENAI_AVAILABLE', True)
    @patch('app.agent.genai.GenerativeModel')
    def test_call_gemini_handles_error(self, mock_model):
        """Test _call_gemini gère les erreurs d'API"""
        mock_model.return_value.generate_content.side_effect = Exception("API Error")
        
        result = _call_gemini("test prompt")
        assert result is None
    
    @patch('app.agent.GENAI_AVAILABLE', True)
    @patch('app.agent.genai.GenerativeModel')
    def test_call_gemini_empty_response(self, mock_model):
        """Test _call_gemini avec réponse vide"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_model.return_value.generate_content.return_value = mock_response
        
        result = _call_gemini("test prompt")
        assert result is None


class TestReformulateAnswer:
    """Tests pour la fonction reformulate_answer()"""
    
    def test_reformulate_with_empty_context(self):
        """Test reformulation avec contexte vide"""
        result = reformulate_answer("Question ?", "")
        assert "information" in result.lower() or "trouvé" in result.lower()
    
    @patch('app.agent.GENAI_AVAILABLE', False)
    def test_reformulate_without_gemini(self):
        """Test reformulation sans Gemini retourne le contexte brut"""
        context = "Informations de l'IMT"
        result = reformulate_answer("Question ?", context)
        assert result == context
    
    @patch('app.agent.GENAI_AVAILABLE', True)
    @patch('app.agent._call_gemini')
    def test_reformulate_with_gemini(self, mock_gemini):
        """Test reformulation avec Gemini"""
        mock_gemini.return_value = "Réponse reformulée"
        result = reformulate_answer("Question ?", "Contexte brut")
        assert result == "Réponse reformulée"
        mock_gemini.assert_called_once()
    
    @patch('app.agent.GENAI_AVAILABLE', True)
    @patch('app.agent._call_gemini')
    def test_reformulate_gemini_fails(self, mock_gemini):
        """Test reformulation quand Gemini échoue"""
        mock_gemini.return_value = None
        context = "Contexte brut"
        result = reformulate_answer("Question ?", context)
        # Doit retourner le contexte brut en fallback
        assert result == context


class TestHeuristics:
    """Tests des heuristiques de décision EMAIL/SEARCH"""
    
    @patch('app.agent.GENAI_AVAILABLE', False)
    def test_email_keywords(self):
        """Test que les mots-clés d'email déclenchent EMAIL"""
        email_phrases = [
            "envoyer un email",
            "contacter le directeur",
            "écrire au directeur",
            "demande officielle",
            "envoye un message"
        ]
        for phrase in email_phrases:
            result = agent(phrase)
            assert "email" in result.lower() or "envoyé" in result.lower() or "simulation" in result.lower()
    
    @patch('app.agent.GENAI_AVAILABLE', False)
    def test_search_keywords(self):
        """Test que les questions de recherche déclenchent SEARCH"""
        search_phrases = [
            "Quelles formations ?",
            "Où est l'IMT ?",
            "Les frais de scolarité",
            "Horaires d'ouverture"
        ]
        for phrase in search_phrases:
            result = agent(phrase)
            assert isinstance(result, str)
            assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
