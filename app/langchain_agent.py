"""
Agent LangChain simplifié pour l'IMT utilisant Gemini.

Version compatible LangChain 1.x - Architecture simple sans ReAct.
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.tools import search_imt, send_email

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

# Prompt système
SYSTEM_PROMPT = """Tu es un assistant IA pour l'IMT (Institut Mines-Télécom) au Sénégal.

Tu peux :
1. Rechercher des informations sur l'IMT (formations, admissions, contact)
2. Envoyer des emails de contact

Directives :
- Réponds TOUJOURS en français
- Sois poli, professionnel et serviable
- Si tu n'es pas sûr, cherche l'information
- Donne des réponses précises et complètes
"""


def create_imt_agent(temperature: float = 0.3, verbose: bool = False):
    """Crée un agent LangChain simple.
    
    Args:
        temperature: Température pour la génération
        verbose: Mode verbeux
        
    Returns:
        Instance ChatGoogleGenerativeAI configurée
        
    Raises:
        ValueError: Si GEMINI_API_KEY manquante
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY ou GOOGLE_API_KEY manquante dans .env")
    
    logger.info("✅ Initialisation agent LangChain avec Gemini")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=temperature,
        google_api_key=api_key
    )
    
    return llm


def run_agent(question: str, agent: Optional[ChatGoogleGenerativeAI] = None) -> str:
    """Exécute l'agent avec une question.
    
    Logique simple :
    1. Détecte si besoin de recherche IMT
    2. Appelle search_imt si nécessaire
    3. Génère réponse avec contexte
    
    Args:
        question: Question utilisateur
        agent: Agent LLM (créé si None)
        
    Returns:
        Réponse générée
    """
    if not question or not question.strip():
        return "Veuillez poser une question valide."
    
    # Créer agent si nécessaire
    if agent is None:
        try:
            agent = create_imt_agent()
        except ValueError as e:
            logger.error(f"Erreur création agent: {e}")
            return "Agent non disponible (clé API manquante)."
    
    try:
        # Détecter besoin de recherche
        keywords_search = ['formation', 'admission', 'contact', 'programme', 
                          'cybersécurité', 'master', 'bachelor', 'imt', 'école']
        needs_search = any(kw in question.lower() for kw in keywords_search)
        
        context = ""
        if needs_search:
            logger.info("🔍 Recherche IMT activée")
            search_results = search_imt(question)
            if search_results:
                context = f"\n\nContexte trouvé :\n{search_results}\n"
        
        # Construire messages
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"{question}{context}")
        ]
        
        # Appeler LLM
        logger.info(f"🤖 Appel Gemini via LangChain")
        response = agent.invoke(messages)
        
        result = response.content.strip()
        logger.info(f"✅ Réponse générée ({len(result)} caractères)")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur agent: {e}")
        return f"Désolé, une erreur s'est produite : {str(e)}"


# Fonction wrapper pour compatibilité
def create_and_run(question: str) -> str:
    """Crée un agent et exécute une question (usage simple)."""
    return run_agent(question)


if __name__ == "__main__":
    # Test rapide
    print("🧪 Test agent LangChain simplifié")
    test_question = "Quelles sont les formations proposées à l'IMT ?"
    response = create_and_run(test_question)
    print(f"\nQuestion: {test_question}")
    print(f"Réponse: {response}")