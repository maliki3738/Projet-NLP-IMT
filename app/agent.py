# app/agent.py

import os
import logging
from dotenv import load_dotenv
from app.tools import search_imt, send_email
from typing import Optional

load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------
# Agent minimal et commenté
# -------------------------
# Principe :
# 1) Tenter d'utiliser le SDK officiel `google.generativeai` (Gemini) si installé.
# 2) Si le SDK n'est pas présent ou si l'appel échoue, utiliser une heuristique simple
#    pour décider entre deux actions : `SEARCH` (répondre) ou `EMAIL` (envoyer un e-mail).
# 3) Les outils `search_imt` et `send_email` restent inchangés et sont appelés selon la décision.

# Tentative d'import du SDK (optionnelle)
try:
    import google.generativeai as genai  # type: ignore
    GENAI_AVAILABLE = True
    API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if API_KEY:
        genai.configure(api_key=API_KEY)
        logger.info("✅ Gemini configuré avec succès")
    else:
        GENAI_AVAILABLE = False
        logger.warning("⚠️  Clé API Gemini manquante - Fallback heuristique activé")
except Exception as e:
    GENAI_AVAILABLE = False
    logger.warning(f"⚠️  Gemini non disponible : {e} - Fallback heuristique activé")

def _call_gemini(prompt: str) -> Optional[str]:
    """Appelle Gemini via le SDK si disponible.

    Retourne la chaîne textuelle de la réponse, ou `None` en cas d'erreur.
    """
    if not GENAI_AVAILABLE:
        logger.debug("Gemini non disponible, retour None")
        return None

    try:
        logger.debug(f"Appel Gemini avec prompt: {prompt[:50]}...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                max_output_tokens=128,
            )
        )
        result = response.text.strip() if response.text else None
        logger.debug(f"Réponse Gemini: {result}")
        return result
    except AttributeError as e:
        logger.error(f"Erreur de structure de réponse Gemini : {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur lors de l'appel Gemini : {e}")
        return None


def agent(question: str) -> str:
    """Fonction principale de l'agent.

    - Construit un prompt simple demandant `SEARCH` ou `EMAIL`.
    - Tente d'obtenir la décision via Gemini (_call_gemini).
    - Si échec, applique une heuristique de mots-clés.
    - Exécute ensuite l'outil approprié et retourne son résultat.
    """
    if not question or not question.strip():
        logger.warning("Question vide reçue")
        return "Désolé, je n'ai pas compris votre question. Pouvez-vous reformuler ?"
    
    logger.info(f"Question reçue : {question}")
    
    try:
        prompt = (
            "Tu es un agent pour l'IMT. Réponds UNIQUEMENT par SEARCH ou EMAIL.\n"
            f"Question : {question}\n"
        )

        decision = _call_gemini(prompt)

        # Si Gemini absent ou problème, heuristique simple basée sur mots-clés
        if not decision:
            logger.info("Utilisation du fallback heuristique")
            q = question.lower()
            # Mots-clés enrichis pour EMAIL
            email_keywords = [
                "directeur", "email", "envoyer", "envoye", "envoi", 
                "contact", "contacter", "écrire", "message", "demande officielle"
            ]
            if any(k in q for k in email_keywords):
                decision = "EMAIL"
            else:
                decision = "SEARCH"

        decision = decision.strip().upper()
        logger.info(f"Décision prise : {decision}")

        if "EMAIL" in decision:
            # Appel de l'outil d'envoi d'email
            logger.info("Exécution : Envoi d'email")
            return send_email(subject="Demande d'informations", content=question)
        
        # Par défaut, on appelle la recherche
        logger.info("Exécution : Recherche IMT")
        raw_context = search_imt(question)
        return reformulate_answer(question, raw_context)
    
    except Exception as e:
        logger.error(f"Erreur critique dans l'agent : {e}", exc_info=True)
        return "Désolé, une erreur s'est produite. Veuillez réessayer ou reformuler votre question."



def reformulate_answer(question: str, context: str) -> str:
    """Reformule la réponse en utilisant Gemini si disponible."""
    if not context or context.strip() == "":
        logger.warning("Contexte vide pour reformulation")
        return "Désolé, je n'ai pas trouvé d'information pertinente sur cette question."
    
    if not GENAI_AVAILABLE:
        # Fallback simple si Gemini indisponible
        logger.debug("Reformulation sans Gemini, retour contexte brut")
        return context

    try:
        prompt = f"""Tu es un assistant clair et concis pour l'Institut des Métiers du Tertiaire (IMT) de Dakar.

À partir des informations suivantes extraites du site de l'IMT Dakar,
réponds simplement et directement à la question.

Question :
{question}

Informations :
{context}

Réponse attendue :
- courte et claire
- en français
- sans événements, dates ou bruit inutile
- si l'information n'est pas dans le contexte, dis-le clairement
"""

        result = _call_gemini(prompt)
        return result if result else context
    except Exception as e:
        logger.error(f"Erreur lors de la reformulation : {e}")
        return context

if __name__ == "__main__":
    print("Agent IMT prêt\n")
    while True:
        question = input("Posez votre question à l'agent IMT (ou 'quit' pour quitter) : ")
        if question.lower() == 'quit':
            break
        response = agent(question)
        print(response)
        print("\n---\n")