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

# Tentative d'import du SDK Gemini (optionnelle)
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
    API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if API_KEY:
        client = genai.Client(api_key=API_KEY)
        logger.info("✅ Gemini configuré avec succès")
    else:
        GENAI_AVAILABLE = False
        logger.warning("⚠️  Clé API Gemini manquante - Fallback heuristique activé")
except Exception as e:
    GENAI_AVAILABLE = False
    logger.warning(f"⚠️  Gemini non disponible : {e} - Fallback heuristique activé")

# Tentative d'import Grok/xAI comme alternative
GROK_AVAILABLE = False
grok_client = None
try:
    import openai
    GROK_API_KEY = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
    if GROK_API_KEY:
        grok_client = openai.OpenAI(
            api_key=GROK_API_KEY,
            base_url="https://api.x.ai/v1"
        )
        GROK_AVAILABLE = True
        logger.info("✅ Grok (xAI) configuré avec succès")
except Exception as e:
    logger.info(f"💡 Grok non disponible : {e}")

# Configuration OpenAI GPT (fallback économique)
OPENAI_AVAILABLE = False
openai_client = None
try:
    import openai
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        OPENAI_AVAILABLE = True
        logger.info("✅ OpenAI GPT configuré avec succès")
except Exception as e:
    logger.info(f"💡 OpenAI non disponible : {e}")

def _call_grok(prompt: str, max_tokens: int = 150) -> Optional[str]:
    """Appelle Grok via l'API xAI.
    
    Args:
        prompt: Le prompt à envoyer
        max_tokens: Nombre max de tokens
    
    Returns:
        La réponse ou None
    """
    if not GROK_AVAILABLE or not grok_client:
        return None
    
    try:
        response = grok_client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Erreur Grok : {e}")
        return None

def _call_openai(prompt: str, max_tokens: int = 200) -> Optional[str]:
    """Appelle OpenAI GPT-4o-mini (économique et performant).
    
    Args:
        prompt: Le prompt à envoyer
        max_tokens: Nombre max de tokens
    
    Returns:
        La réponse ou None
    """
    if not OPENAI_AVAILABLE or not openai_client:
        return None
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Le moins cher : 0.15$/1M tokens entrée, 0.6$/1M sortie
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Erreur OpenAI : {e}")
        return None

def _call_gemini(prompt: str) -> Optional[str]:
    """Appelle les LLMs disponibles avec ordre de priorité intelligent.
    
    Ordre de priorité : Grok → OpenAI → Gemini → None
    
    Instructions pour l'IA:
    Tu es l'expert de l'IMT Dakar. Utilise les documents fournis pour répondre. 
    Si l'information est absente, ne l'invente pas, oriente vers l'administration. 
    Réponds en faisant des phrases complètes et polies.

    Retourne la chaîne textuelle de la réponse, ou `None` en cas d'erreur.
    """
    # Priorité 1 : Essayer Grok si disponible
    if GROK_AVAILABLE:
        result = _call_grok(prompt, max_tokens=150)
        if result:
            return result
        logger.info("🔄 Grok échoué, fallback vers OpenAI...")
    
    # Priorité 2 : Essayer OpenAI (économique)
    if OPENAI_AVAILABLE:
        result = _call_openai(prompt, max_tokens=200)
        if result:
            return result
        logger.info("🔄 OpenAI échoué, fallback vers Gemini...")
    
    # Priorité 3 : Essayer Gemini
    if not GENAI_AVAILABLE:
        logger.debug("Gemini non disponible, retour None")
        return None

    try:
        logger.debug(f"Appel Gemini avec prompt: {prompt[:50]}...")
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=300,
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


def _extract_personal_info(question: str) -> dict:
    """Extrait les informations personnelles de la question.
    
    Returns:
        dict: {entity_type: value} ex: {'name': 'Maliki'}
    """
    import re
    entities = {}
    q_lower = question.lower().strip()
    
    # Ignorer les questions (ne pas extraire de nom)
    question_words = ['comment', 'qui', 'quoi', 'quel', 'quelle', 'où', 'pourquoi', 'quand']
    if any(q_lower.startswith(word) for word in question_words):
        return entities
    
    # Pattern : "je m'appelle X" ou "mon nom est X"
    # Capturer le nom (première lettre majuscule ou pas, on normalisera après)
    name_patterns = [
        r"(?:je m['']appelle|retiens que je m['']appelle)\s+([A-ZÀ-Ÿa-zéèêàâîôûç]+(?:\s+[A-ZÀ-Ÿa-zéèêàâîôûç]+)?)",
        r"mon nom (?:est|c'est)\s+([A-ZÀ-Ÿa-zéèêàâîôûç]+(?:\s+[A-ZÀ-Ÿa-zéèêàâîôûç]+)?)",
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Vérifier que ce n'est pas un mot de question
            if name.lower() not in question_words:
                # Capitaliser le nom proprement
                entities['name'] = ' '.join(word.capitalize() for word in name.split())
                break
    # Pattern : "je suis un/une X" (genre, profil, etc.)
    profile_pattern = r"je suis (?:un|une)\s+(.+?)(?:\.|$|,)"
    profile_match = re.search(profile_pattern, q_lower)
    if profile_match:
        entities['profile'] = profile_match.group(1).strip()
    
    # Pattern email : "mon email est X" ou "mon adresse est X"
    email_pattern = r"mon (?:email|e-mail|adresse|mail) (?:est|c'est)\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    email_match = re.search(email_pattern, q_lower)
    if email_match:
        entities['email'] = email_match.group(1)
    
    # Pattern téléphone : "mon téléphone/numéro est X"
    phone_pattern = r"mon (?:téléphone|numéro|tel) (?:est|c'est)\s+([+]?[0-9\s]+)"
    phone_match = re.search(phone_pattern, q_lower)
    if phone_match:
        entities['phone'] = phone_match.group(1).strip()
    
    return entities


def _answer_personal_question(question: str, entities: dict) -> str:
    """Répond aux questions personnelles en utilisant les entités stockées."""
    q_lower = question.lower().strip()
    
    # Questions sur le nom
    if any(phrase in q_lower for phrase in ["je m'appelle", "mon nom", "comment je", "qui suis-je", "appelle comment"]):
        if 'name' in entities:
            return f"👤 Vous vous appelez **{entities['name']}**."
        else:
            return "Je ne connais pas encore votre nom. Vous pouvez me le dire en disant 'Je m'appelle [votre nom]'."
    
    # Questions sur le profil
    if any(phrase in q_lower for phrase in ["qui suis-je", "je suis qui", "mon profil", "c'est quoi mon profil"]):
        if 'profile' in entities:
            response = f"👤 Vous êtes **{entities['profile']}**."
            if 'name' in entities:
                response = f"👤 Vous vous appelez **{entities['name']}** et vous êtes **{entities['profile']}**."
            return response
    
    # Questions sur l'email
    if any(word in q_lower for word in ["email", "e-mail", "adresse mail"]):
        if 'email' in entities:
            return f"📧 Votre email est **{entities['email']}**."
        else:
            return "Je ne connais pas votre email."
    
    # Questions sur le téléphone
    if any(word in q_lower for word in ["téléphone", "numéro", "tel"]):
        if 'phone' in entities:
            return f"📞 Votre numéro est **{entities['phone']}**."
        else:
            return "Je ne connais pas votre numéro de téléphone."
    
    return None

def agent(question: str, history: list = None, memory_manager=None, session_id: str = None) -> str:
    """Fonction principale de l'agent.

    - Construit un prompt simple demandant `SEARCH` ou `EMAIL`.
    - Tente d'obtenir la décision via Gemini (_call_gemini).
    - Si échec, applique une heuristique de mots-clés.
    - Exécute ensuite l'outil approprié et retourne son résultat.
    """
    if not question or not question.strip():
        logger.warning("Question vide reçue")
        return "Désolé, je n'ai pas compris votre question. Pouvez-vous reformuler ?"
    
    # 1. Extraire et stocker les informations personnelles
    if memory_manager and session_id:
        personal_info = _extract_personal_info(question)
        if personal_info:
            for entity_type, value in personal_info.items():
                memory_manager.set_entity(session_id, entity_type, value)
                logger.info(f"✅ Entité stockée : {entity_type} = {value}")
            
            # Répondre à la confirmation
            if 'name' in personal_info:
                return f"👋 Enchanté **{personal_info['name']}** ! Je vais me souvenir de votre nom."
            elif 'profile' in personal_info:
                return f"✅ J'ai bien noté : vous êtes **{personal_info['profile']}**."
            elif 'email' in personal_info:
                return f"✅ J'ai bien noté votre email : **{personal_info['email']}**"
            elif 'phone' in personal_info:
                return f"✅ J'ai bien noté votre numéro : **{personal_info['phone']}**"
    
    # 2. Vérifier si c'est une question personnelle
    if memory_manager and session_id:
        entities = memory_manager.get_all_entities(session_id)
        personal_answer = _answer_personal_question(question, entities)
        if personal_answer:
            return personal_answer
    
    logger.info(f"Question reçue : {question}")
    
    # 3. Enrichir les questions courtes avec le contexte de la conversation
    enriched_question = question
    if memory_manager and session_id and len(question.split()) <= 3:
        recent_history = memory_manager.get_history(session_id, limit=2)
        if recent_history:
            last_context = ' '.join([msg['content'] for msg in recent_history[-2:] if msg['role'] == 'user'])
            enriched_question = f"{last_context}. {question}"
            logger.info(f"Question enrichie: {enriched_question}")
    
    try:
        prompt = (
            "Tu es un agent pour l'IMT. Réponds UNIQUEMENT par SEARCH ou EMAIL.\n"
            f"Question : {enriched_question}\n"
        )

        decision = _call_gemini(prompt)

        # Si LLM absent ou problème, heuristique simple basée sur mots-clés
        if not decision:
            logger.info("Utilisation du fallback heuristique")
            q = enriched_question.lower()
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
            
            # Extraire le sujet et le message avec les nouvelles regex améliorées
            import re
            subject_match = re.search(r'(?:avec|pour)\s+(?:comme\s+)?(?:pour\s+)?objet\s+["\']([^"\']+)["\']', question, re.IGNORECASE)
            subject = subject_match.group(1) if subject_match else "Demande d'informations"
            
            # Extraire le vrai message si format "envoie un mail avec message X"
            message_match = re.search(r'(?:disant que|avec (?:comme )?message|message)\s+["\']?([^"\']+?)["\']\s*(?:avec|pour|$)', question, re.IGNORECASE)
            if not message_match:
                message_match = re.search(r'(?:disant que|message[\s:]+)(.+?)(?:\s+avec|\s+pour|$)', question, re.IGNORECASE)
            
            content = message_match.group(1).strip() if message_match else question
            
            # Nettoyer le contenu (enlever "avec pour objet..." s'il y est)
            content = re.sub(r'\s*avec\s+pour\s+objet.+$', '', content, flags=re.IGNORECASE)
            
            return send_email(subject=subject, content=content)
        
        # Par défaut, on appelle la recherche
        logger.info("Exécution : Recherche IMT")
        raw_context = search_imt(enriched_question)
        return reformulate_answer(enriched_question, raw_context)
    
    except Exception as e:
        logger.error(f"Erreur critique dans l'agent : {e}", exc_info=True)
        return "Désolé, une erreur s'est produite. Veuillez réessayer ou reformuler votre question."

def _deduplicate_lines(text: str) -> str:
    """Supprime les lignes dupliquées consécutives."""  
    lines = text.split('\n')
    result = []
    prev = None
    for line in lines:
        stripped = line.strip()
        if stripped != prev:
            result.append(line)
            prev = stripped
    return '\n'.join(result)

def reformulate_answer(question: str, context: str) -> str:
    """Reformule la réponse en utilisant Grok/Gemini avec des instructions claires."""
    if not context or context.strip() == "":
        logger.warning("Contexte vide pour reformulation")
        return "Désolé, je n'ai pas trouvé d'information pertinente sur cette question."
    
    # Nettoyer le contexte
    context = _deduplicate_lines(context.strip())
    context = context.replace('===', '').replace('[', '').replace(']', '')
    
    # Essayer avec Grok/Gemini avec prompt amélioré
    prompt = f"""Tu es un assistant expert de l'Institut Mines-Télécom (IMT) à Dakar.

CONTEXTE DOCUMENTAIRE :
{context}

QUESTION DE L'UTILISATEUR :
{question}

INSTRUCTIONS IMPORTANTES :
- Réponds en français de manière claire, concise et professionnelle
- Utilise UNIQUEMENT les informations présentes dans le contexte documentaire
- Si l'information est absente, ne l'invente pas - oriente vers l'administration
- Ne mentionne PAS que tu utilises un contexte ou des documents
- Sois naturel, direct et accueillant comme un conseiller d'études
- Réponds en phrases complètes et polies

RÉPONSE :"""
    
    llm_response = _call_gemini(prompt)
    if llm_response:
        return llm_response
    
    # Fallback intelligent : extraire le meilleur paragraphe du contexte
    logger.info("Utilisation du fallback intelligent")
    lines = [l.strip() for l in context.split('\n') if l.strip() and len(l.strip()) > 40]
    if lines:
        return '\n'.join(lines[:3])  # Retourner les 3 premières lignes pertinentes
    return context[:500]

if __name__ == "__main__":
    print("Agent IMT prêt\n")
    while True:
        question = input("Posez votre question à l'agent IMT (ou 'quit' pour quitter) : ")
        if question.lower() == 'quit':
            break
        response = agent(question)
        print(response)
        print("\n---\n")