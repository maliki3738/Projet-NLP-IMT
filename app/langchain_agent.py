"""
Agent LangChain pour l'IMT utilisant le modèle Gemini.

Ce module implémente un agent ReAct qui peut :
- Rechercher des informations sur l'IMT
- Envoyer des emails de contact

Utilise LangChain pour l'orchestration et le nouveau SDK Gemini.
Intégration Langfuse pour l'observabilité (Jour 4).
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_react_agent
from langchain.agents.agent import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate

from app.langchain_tools import tools

# Langfuse pour l'observabilité
try:
    from langfuse.decorators import observe
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# ========== Configuration Langfuse ==========
if LANGFUSE_AVAILABLE:
    try:
        langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if langfuse_public_key and langfuse_secret_key:
            langfuse_client = Langfuse(
                public_key=langfuse_public_key,
                secret_key=langfuse_secret_key,
                host=langfuse_host
            )
            logger.info("✅ Langfuse configuré avec succès")
        else:
            LANGFUSE_AVAILABLE = False
            logger.warning("⚠️  Clés Langfuse manquantes (LANGFUSE_PUBLIC_KEY ou LANGFUSE_SECRET_KEY)")
    except Exception as e:
        LANGFUSE_AVAILABLE = False
        logger.warning(f"⚠️  Erreur configuration Langfuse : {e}")
else:
    logger.info("ℹ️  Langfuse non installé (optionnel)")


# Template de prompt pour l'agent ReAct
AGENT_PROMPT = """Tu es un assistant IA pour l'IMT (Institut des Métiers du Tertiaire) au Sénégal.

Tu as accès aux outils suivants :

{tools}

Utilise le format suivant pour répondre :

Question: la question de l'utilisateur
Thought: ce que tu dois faire
Action: l'outil à utiliser, doit être l'un de [{tool_names}]
Action Input: l'entrée pour l'outil
Observation: le résultat de l'outil
... (ce cycle Thought/Action/Action Input/Observation peut se répéter)
Thought: Je sais maintenant comment répondre
Final Answer: la réponse finale en français

Directives importantes :
- Réponds TOUJOURS en français
- Sois poli, professionnel et serviable
- Si tu n'es pas sûr, utilise search_imt pour chercher l'information
- Pour les demandes de contact, utilise send_email
- Si les informations ne sont pas dans la base, dis-le clairement
- Donne des réponses précises et complètes

Question: {input}
{agent_scratchpad}
"""


def create_imt_agent(
    temperature: float = 0.7,
    max_iterations: int = 5,
    verbose: bool = True
) -> AgentExecutor:
    """Crée un agent LangChain pour l'IMT.
    
    Args:
        temperature: Température pour la génération (0.0 = déterministe, 1.0 = créatif)
        max_iterations: Nombre maximum d'itérations de l'agent
        verbose: Si True, affiche les étapes de raisonnement
        
    Returns:
        AgentExecutor configuré et prêt à utiliser
        
    Raises:
        ValueError: Si GEMINI_API_KEY n'est pas définie
    """
    # Vérifier la clé API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY non trouvée dans les variables d'environnement")
        raise ValueError(
            "GEMINI_API_KEY manquante. "
            "Configurez-la dans le fichier .env"
        )
    
    logger.info("Initialisation de l'agent LangChain avec Gemini")
    
    # Initialiser le modèle Gemini via LangChain
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # Compatible avec google-genai (nouvelle API v1)
        temperature=temperature,
        google_api_key=api_key
    )
    
    # Créer le prompt
    prompt = PromptTemplate.from_template(AGENT_PROMPT)
    
    # Créer l'agent ReAct
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Créer l'executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        max_iterations=max_iterations,
        handle_parsing_errors=True,  # Gérer les erreurs de parsing
        return_intermediate_steps=False
    )
    
    logger.info(f"Agent créé avec {len(tools)} outils: {[t.name for t in tools]}")
    return agent_executor


def run_agent(question: str, agent: Optional[AgentExecutor] = None) -> str:
    """Exécute l'agent avec une question.
    
    Args:
        question: La question de l'utilisateur
        agent: L'agent à utiliser (si None, en crée un nouveau)
        
    Returns:
        La réponse de l'agent
    """
    # Validation de la question
    if not question or not question.strip():
        logger.warning("Question vide reçue")
        return "Veuillez poser une question valide."
    
    # Créer un agent si nécessaire
    if agent is None:
        try:
            agent = create_imt_agent()
        except ValueError as e:
            logger.error(f"Impossible de créer l'agent: {e}")
            return (
                "Désolé, l'agent ne peut pas être initialisé. "
                "Vérifiez la configuration de GEMINI_API_KEY."
            )
    
    # Exécuter l'agent
    try:
        logger.info(f"Exécution agent avec question: {question}")
        result = agent.invoke({"input": question})
        
        # Extraire la réponse
        if isinstance(result, dict):
            answer = result.get("output", str(result))
        else:
            answer = str(result)
        
        logger.info("Réponse générée avec succès")
        return answer
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'agent: {e}", exc_info=True)
        return (
            f"Désolé, une erreur s'est produite : {str(e)}\n"
            "Veuillez réessayer ou reformuler votre question."
        )


# Point d'entrée pour tests
if __name__ == "__main__":
    print("🤖 Agent IMT LangChain - Mode Test\n")
    print("Questions d'exemple :")
    print("1. Quelles sont les formations disponibles à l'IMT ?")
    print("2. Où se trouve l'IMT ?")
    print("3. Envoie un email au directeur pour demander des informations\n")
    
    # Créer l'agent
    try:
        agent = create_imt_agent(verbose=True)
        
        # Boucle interactive
        while True:
            question = input("\nVous : ").strip()
            if not question or question.lower() in ['exit', 'quit', 'q']:
                print("Au revoir !")
                break
                
            response = run_agent(question, agent)
            print(f"\nAgent : {response}")
            
    except KeyboardInterrupt:
        print("\n\nAu revoir !")
    except Exception as e:
        logger.error(f"Erreur fatale: {e}", exc_info=True)
        print(f"\nErreur : {e}")
