"""
LangChain Tools pour l'agent IMT.

Ce module transforme les fonctions de tools.py en LangChain Tools
pour être utilisés par un agent ReAct.
"""
import logging
from langchain.tools import tool
from typing import Optional

# Import des fonctions originales
from app.tools import search_imt as _search_imt_original
from app.tools import send_email as _send_email_original

logger = logging.getLogger(__name__)


@tool
def search_imt(query: str) -> str:
    """Recherche des informations sur l'IMT Sénégal.
    
    Utilise cette fonction pour trouver des informations sur :
    - Les formations disponibles à l'IMT
    - Les frais de scolarité et coûts
    - L'emplacement et les coordonnées de contact
    - Le processus d'admission
    - Les programmes et cursus
    - Les infrastructures (Edulab, etc.)
    
    Args:
        query: La question ou les mots-clés à rechercher
        
    Returns:
        Les informations trouvées dans la base de connaissances IMT
        
    Examples:
        >>> search_imt("formations disponibles")
        >>> search_imt("frais de scolarité")
        >>> search_imt("où se trouve l'IMT")
    """
    logger.info(f"LangChain Tool search_imt appelé avec query: {query}")
    return _search_imt_original(query)


@tool
def send_email(subject: str, content: str, recipient: Optional[str] = None) -> str:
    """Envoie un email de contact à l'IMT.
    
    Utilise cette fonction quand l'utilisateur veut :
    - Contacter le directeur de l'IMT
    - Demander des informations supplémentaires
    - Poser une question qui nécessite une réponse officielle
    - Faire une demande d'admission ou d'informations
    
    Args:
        subject: Le sujet de l'email
        content: Le contenu/corps de l'email
        recipient: Adresse email du destinataire (optionnel)
        
    Returns:
        Confirmation d'envoi ou message d'erreur
        
    Examples:
        >>> send_email("Demande d'informations", "Je voudrais en savoir plus sur...")
        >>> send_email("Candidature", "Voici ma demande d'admission", "directeur@imt.sn")
    """
    logger.info(f"LangChain Tool send_email appelé - sujet: {subject}")
    return _send_email_original(subject, content, recipient)


# Liste des outils pour l'agent LangChain
tools = [search_imt, send_email]


# Fonction helper pour obtenir les noms des outils
def get_tool_names() -> list[str]:
    """Retourne la liste des noms d'outils disponibles."""
    return [tool.name for tool in tools]
