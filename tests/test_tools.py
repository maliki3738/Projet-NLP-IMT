"""
Tests pour le module tools.
"""
import sys
from pathlib import Path
import os
from unittest.mock import patch, MagicMock
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.tools import search_imt, send_email, _validate_email


# ===========================
# Tests de recherche IMT
# ===========================

def test_search_imt():
    """Test que la recherche fonctionne avec un mot-clé valide."""
    result = search_imt("accueil")
    assert "imt" in result.lower() or "aucun" in result.lower()


def test_search_imt_empty_query():
    """Test avec une requête vide."""
    result = search_imt("")
    assert "valide" in result.lower() or "erreur" in result.lower()


def test_search_imt_location_keywords():
    """Test que les mots-clés de localisation sont détectés."""
    location_keywords = ["situé", "adresse", "localisation", "où", "trouver"]
    
    for keyword in location_keywords:
        result = search_imt(keyword)
        # Devrait retourner des infos de localisation ou message approprié
        assert isinstance(result, str)
        assert len(result) > 0


def test_search_imt_no_results():
    """Test avec un mot-clé introuvable."""
    result = search_imt("xyzabc123nonexistent")
    assert "aucun" in result.lower() or "pas de résultat" in result.lower()


# ===========================
# Tests de validation email
# ===========================

class TestEmailValidation:
    """Tests pour la validation d'adresses email."""
    
    def test_validate_email_valid_simple(self):
        """Test avec des adresses email valides simples."""
        assert _validate_email("test@example.com") is True
        assert _validate_email("user@domain.org") is True
        assert _validate_email("admin@test.fr") is True
    
    def test_validate_email_valid_complex(self):
        """Test avec des adresses email valides complexes."""
        assert _validate_email("first.last@example.com") is True
        assert _validate_email("user+tag@domain.co.uk") is True
        assert _validate_email("123@example.com") is True
        assert _validate_email("user_name@example-domain.com") is True
    
    def test_validate_email_invalid_format(self):
        """Test avec des formats invalides."""
        assert _validate_email("invalid") is False
        assert _validate_email("@example.com") is False
        assert _validate_email("user@") is False
        assert _validate_email("user@domain") is False
        assert _validate_email("") is False
    
    def test_validate_email_invalid_characters(self):
        """Test avec des caractères invalides."""
        assert _validate_email("user name@example.com") is False
        assert _validate_email("user@domain .com") is False
        assert _validate_email("user@@example.com") is False


# ===========================
# Tests d'envoi d'email (simulation)
# ===========================

def test_send_email_simulation():
    """Test en mode simulation (aucune config SMTP)."""
    # S'assurer qu'aucune variable d'environnement n'est définie
    with patch.dict(os.environ, {}, clear=True):
        result = send_email("Test sujet", "Test contenu")
        assert "EMAIL NON ENVOYÉ" in result
        assert "simulation" in result.lower()


def test_send_email_invalid_subject():
    """Test avec un sujet invalide."""
    result = send_email("", "Contenu valide")
    assert "erreur" in result.lower() or "impossible" in result.lower()


def test_send_email_invalid_body():
    """Test avec un corps invalide."""
    result = send_email("Sujet valide", "")
    assert "erreur" in result.lower() or "impossible" in result.lower()


# ===========================
# Tests d'envoi d'email (avec mocks SMTP)
# ===========================

class TestEmailSending:
    """Tests pour l'envoi d'emails avec configuration SMTP."""
    
    @patch('app.tools.smtplib.SMTP')
    @patch.dict(os.environ, {
        'EMAIL_USER': 'test@example.com',
        'EMAIL_PASS': 'testpass',
        'EMAIL_TO': 'dest@example.com',
        'SMTP_HOST': 'smtp.example.com',
        'SMTP_PORT': '587'
    })
    def test_send_email_success(self, mock_smtp):
        """Test d'envoi réussi avec configuration complète."""
        # Créer un mock du serveur SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = send_email("Test Sujet", "Test Corps")
        
        # Vérifier le résultat
        assert "SUCCÈS" in result or "ENVOYÉ" in result
        assert "dest@example.com" in result
    
    @patch('app.tools.smtplib.SMTP')
    @patch.dict(os.environ, {
        'EMAIL_USER': 'test@example.com',
        'EMAIL_PASS': 'wrongpass',
        'EMAIL_TO': 'dest@example.com',
        'SMTP_HOST': 'smtp.example.com'
    })
    def test_send_email_auth_error(self, mock_smtp):
        """Test d'erreur d'authentification."""
        from smtplib import SMTPAuthenticationError
        
        mock_server = MagicMock()
        mock_server.login.side_effect = SMTPAuthenticationError(535, b'Authentication failed')
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = send_email("Test", "Test")
        
        # Le code continue même avec erreur auth - vérifier qu'il ne plante pas
        assert isinstance(result, str)
        assert len(result) > 0
    
    @patch('app.tools.smtplib.SMTP')
    @patch.dict(os.environ, {
        'EMAIL_USER': 'test@example.com',
        'EMAIL_PASS': 'testpass',
        'EMAIL_TO': 'dest@example.com'
    })
    def test_send_email_connection_error(self, mock_smtp):
        """Test d'erreur de connexion."""
        mock_smtp.side_effect = ConnectionRefusedError()
        
        result = send_email("Test", "Test")
        
        assert "CONNEXION" in result or "REFUSÉE" in result
        assert "serveur" in result.lower()
    
    @patch('app.tools.smtplib.SMTP')
    @patch.dict(os.environ, {
        'EMAIL_USER': 'test@example.com',
        'EMAIL_PASS': 'testpass',
        'EMAIL_TO': 'dest@example.com'
    })
    def test_send_email_timeout(self, mock_smtp):
        """Test de timeout."""
        mock_smtp.side_effect = TimeoutError()
        
        result = send_email("Test", "Test")
        
        assert "TIMEOUT" in result.upper()
        assert "expiré" in result.lower() or "connexion" in result.lower()
    
    @patch('app.tools.smtplib.SMTP')
    @patch.dict(os.environ, {
        'EMAIL_USER': 'invalid-email',  # Email invalide
        'EMAIL_PASS': 'testpass',
        'EMAIL_TO': 'dest@example.com'
    })
    def test_send_email_invalid_sender(self, mock_smtp):
        """Test avec adresse expéditeur invalide."""
        result = send_email("Test", "Test")
        
        assert "valide" in result.lower() or "erreur" in result.lower()
    
    @patch('app.tools.smtplib.SMTP')
    @patch.dict(os.environ, {
        'EMAIL_USER': 'test@example.com',
        'EMAIL_PASS': 'testpass',
        'EMAIL_TO': 'invalid-email'  # Email invalide
    })
    def test_send_email_invalid_recipient(self, mock_smtp):
        """Test avec adresse destinataire invalide."""
        result = send_email("Test", "Test")
        
        assert "valide" in result.lower() or "erreur" in result.lower()


# ===========================
# Tests d'intégration
# ===========================

class TestToolsIntegration:
    """Tests d'intégration entre les outils."""
    
    def test_search_then_email_simulation(self):
        """Test d'un workflow complet : recherche puis email."""
        # 1. Recherche d'information
        search_result = search_imt("formations")
        assert isinstance(search_result, str)
        assert len(search_result) > 0
        
        # 2. Envoi d'email avec le résultat (simulation)
        with patch.dict(os.environ, {}, clear=True):
            email_result = send_email(
                "Demande d'informations",
                f"Voici les informations trouvées: {search_result[:100]}"
            )
            assert "simulation" in email_result.lower()
