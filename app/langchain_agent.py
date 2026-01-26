"""
Agent LangChain intelligent pour l'IMT utilisant Gemini avec function calling.

Version compatible LangChain 1.x - Architecture intelligente avec outils.
"""
import os
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool

from app.tools import search_imt as _search_imt_original
from app.tools import send_email as _send_email_original

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

# Définition des outils LangChain
@tool
def search_imt(query: str) -> str:
    """Recherche des informations sur l'IMT (formations, admissions, programmes, contact).
    
    Utilise cette fonction quand l'utilisateur demande :
    - Les formations disponibles
    - Les conditions d'admission
    - Les programmes d'études
    - Les informations de contact
    - Toute information sur l'IMT
    
    Args:
        query: La question de l'utilisateur sur l'IMT
        
    Returns:
        Les informations trouvées dans la base de connaissances
    """
    logger.info(f"🔍 Outil search_imt appelé avec: {query[:50]}...")
    return _search_imt_original(query)

@tool
def send_email(subject: str, content: str, recipient: Optional[str] = None) -> str:
    """Envoie un email de contact à l'IMT.
    
    Utilise cette fonction quand l'utilisateur veut :
    - Envoyer une demande d'information
    - Contacter l'administration
    - Poser une question nécessitant une réponse personnalisée
    
    Args:
        subject: Sujet de l'email
        content: Contenu du message
        recipient: Email du destinataire (optionnel)
        
    Returns:
        Confirmation d'envoi ou erreur
    """
    logger.info(f"📧 Outil send_email appelé: {subject}")
    return _send_email_original(subject, content, recipient)

# Liste des outils disponibles
TOOLS = [search_imt, send_email]

# Prompt système amélioré
SYSTEM_PROMPT = """Tu es un assistant IA intelligent pour l'IMT (Institut Mines-Télécom) au Sénégal.

Tu as accès à des outils pour t'aider à répondre :
- search_imt : Recherche dans la base de connaissances de l'IMT
- send_email : Envoie un email de contact à l'IMT

CAPACITÉS DE RAISONNEMENT :
1. Analyse la question pour comprendre l'intention
2. Décide SI tu as besoin d'utiliser un outil :
   - Pour des questions sur formations/programmes/admission → utilise search_imt
   - Pour des demandes de contact personnalisé → utilise send_email
   - Pour des questions générales/salutations → réponds directement
3. Synthétise les informations de manière claire et structurée

DIRECTIVES :
- Réponds TOUJOURS en français
- Sois poli, professionnel et serviable
- Raisonne étape par étape pour les questions complexes
- Si tu utilises un outil, explique pourquoi
- Donne des réponses précises, complètes et bien formatées
- Si tu ne sais pas, dis-le honnêtement et propose d'utiliser search_imt

EXEMPLES DE RAISONNEMENT :
Q: "Quelles formations proposez-vous ?"
→ Je dois chercher dans la base : utiliser search_imt("formations")

Q: "Bonjour, comment allez-vous ?"
→ Salutation simple : répondre directement sans outil

Q: "Je veux m'inscrire en cybersécurité"
→ Besoin d'infos admission : utiliser search_imt("admission cybersécurité")
"""


def create_imt_agent(temperature: float = 0.3, verbose: bool = False):
    """Crée un agent LangChain intelligent avec function calling.
    
    Args:
        temperature: Température pour la génération (0.0-1.0)
        verbose: Mode verbeux pour debug
        
    Returns:
        Instance ChatGoogleGenerativeAI avec outils liés
        
    Raises:
        ValueError: Si GEMINI_API_KEY manquante
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY ou GOOGLE_API_KEY manquante dans .env")
    
    logger.info("✅ Initialisation agent LangChain INTELLIGENT avec Gemini")
    
    # Créer le LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=temperature,
        google_api_key=api_key,
        verbose=verbose
    )
    
    # Lier les outils au LLM (function calling)
    llm_with_tools = llm.bind_tools(TOOLS)
    
    logger.info(f"🛠️  {len(TOOLS)} outils liés : {[t.name for t in TOOLS]}")
    
    return llm_with_tools


def run_agent(question: str, agent: Optional[ChatGoogleGenerativeAI] = None, 
              max_iterations: int = 3) -> str:
    """Exécute l'agent avec raisonnement intelligent et function calling.
    
    L'agent va :
    1. Analyser la question
    2. Décider s'il a besoin d'appeler un outil
    3. Appeler l'outil si nécessaire
    4. Synthétiser une réponse finale
    
    Args:
        question: Question utilisateur
        agent: Agent LLM avec outils (créé si None)
        max_iterations: Nombre max d'appels d'outils (sécurité)
        
    Returns:
        Réponse générée intelligemment
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
        # Historique de la conversation
        messages: List[Any] = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=question)
        ]
        
        iteration = 0
        
        # Boucle de raisonnement avec outils
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"🧠 Itération {iteration}: Appel Gemini...")
            
            # Appeler le LLM
            response = agent.invoke(messages)
            
            # Vérifier si Gemini veut appeler un outil
            tool_calls = getattr(response, 'tool_calls', None) or []
            
            if not tool_calls:
                # Pas d'outil à appeler → réponse finale
                logger.info(f"✅ Réponse finale générée ({len(response.content)} caractères)")
                return response.content.strip()
            
            # Gemini veut appeler des outils
            logger.info(f"🛠️  {len(tool_calls)} outil(s) à appeler")
            messages.append(response)  # Ajouter la réponse de Gemini
            
            # Exécuter chaque outil demandé
            for tool_call in tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call.get('args', {})
                
                logger.info(f"⚙️  Exécution: {tool_name}({tool_args})")
                
                # Trouver et exécuter l'outil
                tool_result = None
                for tool_obj in TOOLS:
                    if tool_obj.name == tool_name:
                        tool_result = tool_obj.invoke(tool_args)
                        break
                
                if tool_result is None:
                    tool_result = f"Erreur: outil '{tool_name}' non trouvé"
                
                # Ajouter le résultat de l'outil à l'historique
                from langchain_core.messages import ToolMessage
                messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call.get('id', 'unknown')
                    )
                )
                
                logger.info(f"✅ Résultat outil: {str(tool_result)[:100]}...")
        
        # Si on sort de la boucle sans réponse finale
        logger.warning(f"⚠️  Max iterations atteint ({max_iterations})")
        return "Désolé, je n'ai pas pu terminer le traitement de votre question."
        
    except Exception as e:
        logger.error(f"❌ Erreur agent: {e}", exc_info=True)
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