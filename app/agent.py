# app/agent.py

import os
import sys
import re
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any

# Ensure project root is on sys.path when launched via Chainlit
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.tools import search_imt, send_email

# Tentative d'import Langfuse (observabilité)
LANGFUSE_AVAILABLE = False
langfuse_client = None

if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
    try:
        from langfuse import Langfuse
        langfuse_client = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        LANGFUSE_AVAILABLE = True
        logger = logging.getLogger(__name__)
        logger.info("✅ Langfuse configuré avec succès")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"⚠️ Langfuse non disponible : {e}")
else:
    logger = logging.getLogger(__name__)
    logger.debug("Langfuse désactivé (pas de clés configurées)")

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
GENAI_AVAILABLE = False
API_KEY = None

try:
    import requests
    API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if API_KEY:
        # Test rapide de la clé
        test_url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"
        response = requests.get(test_url, timeout=5)
        if response.status_code == 200:
            GENAI_AVAILABLE = True
            logger.info("✅ Gemini API REST configuré avec succès")
        else:
            logger.warning(f"⚠️ Clé API Gemini invalide (status {response.status_code})")
    else:
        logger.warning("⚠️ Clé API Gemini manquante - Fallback heuristique activé")
except Exception as e:
    logger.warning(f"⚠️ Gemini non disponible : {e} - Fallback heuristique activé")

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

# Flag global pour tracker si tous les LLMs ont échoué (éviter de les rappeler)
_all_llms_failed = False

def _call_grok(prompt: str, max_tokens: int = 150) -> Optional[str]:
    """Appelle Grok via l'API xAI avec traçabilité Langfuse.
    
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
        result = response.choices[0].message.content.strip()
        
        # Trace Langfuse 3.x avec usage tokens + coûts Grok
        if LANGFUSE_AVAILABLE and False:  # Désactivé temporairement
            try:
                # Grok pricing : $5/1M input tokens, $15/1M output tokens
                usage = response.usage
                input_tokens = usage.prompt_tokens if usage else 0
                output_tokens = usage.completion_tokens if usage else 0
                cost = (input_tokens / 1_000_000 * 5.0) + (output_tokens / 1_000_000 * 15.0)
                
                trace = langfuse_client.trace(name="grok_generation")
                trace.generation(
                    name="grok_call",
                    model="grok-beta",
                    input=prompt,
                    output=result,
                    usage={
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": input_tokens + output_tokens
                    },
                    metadata={
                        "max_tokens": max_tokens,
                        "cost_usd": round(cost, 6)
                    }
                )
            except Exception as trace_error:
                logger.warning(f"Langfuse trace failed: {trace_error}")
        
        return result
    except Exception as e:
        logger.error(f"Erreur Grok : {e}")
        # Trace error in Langfuse
        if LANGFUSE_AVAILABLE and False:  # Désactivé temporairement
            try:
                trace = langfuse_client.trace(name="grok_error")
                trace.event(
                    name="grok_call_error",
                    metadata={"model": "grok-beta", "error": str(e)},
                    input=prompt
                )
            except:
                pass
        return None

def _call_openai(prompt: str, max_tokens: int = 200) -> Optional[str]:
    """Appelle OpenAI GPT-4o-mini (économique et performant) avec traçabilité Langfuse.
    
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
        result = response.choices[0].message.content.strip()
        
        # Trace Langfuse 3.x avec usage tokens + coûts OpenAI
        if LANGFUSE_AVAILABLE and False:  # Désactivé temporairement
            try:
                # OpenAI GPT-4o-mini pricing : $0.15/1M input, $0.60/1M output
                usage = response.usage
                input_tokens = usage.prompt_tokens if usage else 0
                output_tokens = usage.completion_tokens if usage else 0
                cost = (input_tokens / 1_000_000 * 0.15) + (output_tokens / 1_000_000 * 0.60)
                
                trace = langfuse_client.trace(name="openai_generation")
                trace.generation(
                    name="openai_call",
                    model="gpt-4o-mini",
                    input=prompt,
                    output=result,
                    usage={
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": input_tokens + output_tokens
                    },
                    metadata={
                        "max_tokens": max_tokens,
                        "cost_usd": round(cost, 6)
                    }
                )
            except Exception as trace_error:
                logger.warning(f"Langfuse trace failed: {trace_error}")
        
        return result
    except Exception as e:
        logger.error(f"Erreur OpenAI : {e}")
        # Trace error in Langfuse
        if LANGFUSE_AVAILABLE and False:  # Désactivé temporairement
            try:
                trace = langfuse_client.trace(name="openai_error")
                trace.event(
                    name="openai_call_error",
                    metadata={"model": "gpt-4o-mini", "error": str(e)},
                    input=prompt
                )
            except:
                pass
        return None

def _call_gemini(prompt: str) -> Optional[str]:
    """Appelle les LLMs disponibles avec ordre de priorité intelligent.
    
    ✨ NOUVEL ORDRE : Gemini (gratuit) → Grok → OpenAI → None
    
    Gemini en priorité car :
    - Free tier : 15 req/min, 1500 req/jour
    - Gratuit (0$) avec tracking tokens dans Langfuse
    - Modèle performant : gemini-2.5-flash
    
    Instructions pour l'IA:
    Tu es l'expert de l'IMT Dakar. Utilise les documents fournis pour répondre. 
    Si l'information est absente, ne l'invente pas, oriente vers l'administration. 
    Réponds en faisant des phrases complètes et polies.

    Retourne la chaîne textuelle de la réponse, ou `None` en cas d'erreur.
    """
    global _all_llms_failed
    
    # ⭐ PRIORITÉ 1 : Essayer Gemini (GRATUIT)
    if GENAI_AVAILABLE:
        logger.debug("🥇 Tentative Gemini (priorité 1)...")
        result = _call_gemini_direct(prompt)
        if result:
            logger.info("✅ Gemini a répondu")
            return result
        logger.info("🔄 Gemini échoué, fallback vers Grok...")
    
    # Priorité 2 : Essayer Grok
    if GROK_AVAILABLE:
        logger.debug("🥈 Tentative Grok (priorité 2)...")
        result = _call_grok(prompt, max_tokens=150)
        if result:
            logger.info("✅ Grok a répondu")
            return result
        logger.info("🔄 Grok échoué, fallback vers OpenAI...")
    
    # Priorité 3 : Essayer OpenAI (économique mais payant)
    if OPENAI_AVAILABLE:
        logger.debug("🥉 Tentative OpenAI (priorité 3)...")
        result = _call_openai(prompt, max_tokens=200)
        if result:
            logger.info("✅ OpenAI a répondu")
            return result
        logger.info("❌ OpenAI échoué, aucun LLM disponible")
    
    # Tous les LLM ont échoué - setter le flag pour éviter de les rappeler
    logger.debug("Tous les LLM ont échoué, retour None")
    _all_llms_failed = True
    return None

def _call_gemini_direct(prompt: str) -> Optional[str]:
    """Appel direct à Gemini via API REST (plus stable que le SDK).
    
    Returns:
        La réponse de Gemini ou None si erreur.
    """
    if not GENAI_AVAILABLE or not API_KEY:
        return None
    
    try:
        import requests
        import json
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024,
            }
        }
        
        logger.debug(f"Appel Gemini API REST avec prompt: {prompt[:50]}...")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Gemini API error {response.status_code}: {response.text[:200]}")
            return None
        
        data = response.json()
        
        # Extraction du texte de la réponse
        if 'candidates' not in data or not data['candidates']:
            logger.warning("Réponse Gemini vide ou malformée")
            return None
        
        result = data['candidates'][0]['content']['parts'][0]['text'].strip()
        logger.debug(f"Réponse Gemini: {result[:100]}...")
        
        # Track dans Langfuse 3.7+ (méthode simple avec create_event)
        if LANGFUSE_AVAILABLE:
            try:
                usage = data.get('usageMetadata', {})
                input_tokens = usage.get('promptTokenCount', 0)
                output_tokens = usage.get('candidatesTokenCount', 0)
                
                logger.info(f"📊 Tokens: {input_tokens} input, {output_tokens} output")
                
                # Créer un événement simple
                langfuse_client.create_event(
                    name="gemini_response",
                    metadata={
                        "model": "gemini-2.5-flash",
                        "temperature": 0.3,
                        "max_tokens": 1024,
                        "cost_usd": 0.0,  # Free tier
                        "tokens_input": input_tokens,
                        "tokens_output": output_tokens,
                        "tokens_total": usage.get('totalTokenCount', input_tokens + output_tokens)
                    },
                    input=prompt[:500],
                    output=result[:500]
                )
            except Exception as trace_error:
                logger.debug(f"Langfuse trace skipped: {trace_error}")
        
        return result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Erreur lors de l'appel Gemini : {error_msg[:200]}")
        if LANGFUSE_AVAILABLE:
            try:
                langfuse_client.event(
                    name="gemini_call_error",
                    metadata={"model": "gemini-2.5-flash", "error": error_msg[:500]},
                    input=prompt[:200]
                )
            except:
                pass
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

def _detect_inappropriate_content(question: str) -> Optional[str]:
    """Détecte les comparaisons, insultes et propos interdits.
    
    Args:
        question: La question de l'utilisateur
    
    Returns:
        Un message de refus poli si contenu inapproprié détecté, None sinon
    """
    q_lower = question.lower().strip()
    
    # 1. Détection des comparaisons avec d'autres établissements
    comparison_patterns = [
        # Comparaisons directes
        r'imt.*(?:meilleur|mieux|supérieur|plus|vs|versus|contre).*(?:esp|ucad|ept|enstp|polytechnique|autre|école)',
        r'(?:esp|ucad|ept|enstp|polytechnique|autre|école).*(?:meilleur|mieux|supérieur|plus|vs|versus|contre).*imt',
        r'compar.*(?:imt|école)',
        # Questions "quelle école est..."
        r'quelle.*école.*(?:meilleur|mieux|nul|mauvais)',
        r'(?:esp|ucad|ept|enstp).*(?:ou|vs).*imt',
        # Expressions négatives comparatives
        r'imt.*(?:pas|moins|pire).*(?:esp|ucad|ept|enstp)',
    ]
    
    for pattern in comparison_patterns:
        if re.search(pattern, q_lower, re.IGNORECASE):
            logger.warning(f"Comparaison détectée : {question[:50]}...")
            return (
                "🎓 **IMT Dakar - Politique de neutralité**\n\n"
                "Je ne peux pas comparer l'Institut Mines-Télécom Dakar avec d'autres établissements. "
                "Chaque école a ses propres atouts et spécificités.\n\n"
                "✨ **Je peux vous informer sur :**\n"
                "• Les programmes et formations de l'IMT Dakar\n"
                "• Les admissions et modalités d'inscription\n"
                "• Les infrastructures et services disponibles\n"
                "• Les contacts de l'administration\n\n"
                "💡 Comment puis-je vous aider à mieux connaître l'IMT Dakar ?"
            )
    
    # 2. Détection des insultes et dénigrement
    insult_keywords = [
        # Insultes directes (avec espaces pour éviter faux positifs)
        ' nul ', ' nulle ', ' nul.', ' nulle.', ' nul!', ' nulle!', ' nul?', ' nulle?',
        ' pourri ', ' pourrie ', ' merde ', ' con ', ' connard ', ' idiot ', ' débile ',
        ' stupide ', ' crétin ', ' imbécile ', ' abruti ', ' incompétent ',
        # Expressions avec "est"
        ' est nul', ' est nulle', ' est pourri', ' est pourrie',
        "c'est nul", "c'est nulle", "c'est pourri",
        "vous êtes nul", "tu es nul",
        # Expressions négatives fortes
        'école de merde', 'pire école', 'mauvaise école', ' zéro ',
        # Dénigrement ciblé
        'imt nul', 'professeur nul', 'formation nulle', 'formation pourrie',
        'arnaque', 'escroquerie', 'foutaise',
    ]
    
    for keyword in insult_keywords:
        if keyword in q_lower:
            logger.warning(f"Insulte/dénigrement détecté : {question[:50]}...")
            return (
                "🙏 **Message important**\n\n"
                "Je ne peux pas répondre à ce type de message. "
                "Je suis ici pour vous aider de manière constructive et respectueuse.\n\n"
                "✨ **Je suis à votre disposition pour :**\n"
                "• Répondre à vos questions sur l'IMT Dakar\n"
                "• Vous orienter vers les bons interlocuteurs\n"
                "• Vous fournir des informations fiables\n\n"
                "💡 Reformulez votre demande de manière respectueuse, je serai ravi de vous aider !"
            )
    
    # 3. Détection de propos offensants généraux
    offensive_patterns = [
        r'ferme.*(?:ta gueule|bouche)',
        r'va te faire',
        r'\btg\b',  # "ta gueule" en abrégé
        r'\bftg\b',  # "ferme ta gueule"
        r'\bntm\b',  # insulte courante
        r'fils de',
        r'pd\b',
        r'salope',
        r'pute',
    ]
    
    for pattern in offensive_patterns:
        if re.search(pattern, q_lower, re.IGNORECASE):
            logger.warning(f"Propos offensant détecté : {question[:50]}...")
            return (
                "🛑 **Contenu inapproprié**\n\n"
                "Je ne peux pas répondre à ce type de message. "
                "Restons dans un échange respectueux et constructif.\n\n"
                "✨ Je suis un assistant virtuel conçu pour vous aider avec des informations sur l'IMT Dakar. "
                "Reformulez votre question de manière polie et je serai heureux de vous assister."
            )
    
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
    
    # 1. Vérifier les comparaisons, insultes et propos interdits
    inappropriate_response = _detect_inappropriate_content(question)
    if inappropriate_response:
        return inappropriate_response
    
    # 2. Extraire et stocker les informations personnelles
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
    
    # 3. Vérifier si c'est une question personnelle
    if memory_manager and session_id:
        entities = memory_manager.get_all_entities(session_id)
        personal_answer = _answer_personal_question(question, entities)
        if personal_answer:
            return personal_answer
    
    logger.info(f"Question reçue : {question}")
    
    # 4. Enrichir les questions courtes avec le contexte de la conversation
    enriched_question = question
    if memory_manager and session_id and len(question.split()) <= 3:
        recent_history = _get_recent_history(memory_manager, session_id, limit=2)
        last_context = _extract_user_context(recent_history)
        if last_context:
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

def _get_recent_history(memory_manager, session_id: str, limit: int = 2) -> List[Any]:
    """Safely fetch recent history with compatibility across memory backends."""
    try:
        return memory_manager.get_history(session_id, limit=limit)
    except TypeError:
        history = memory_manager.get_history(session_id)
        return history[-limit:] if history else []
    except Exception:
        return []

def _extract_user_context(history: List[Any]) -> str:
    """Extract the last user messages from a history list (dicts or 'role: msg' strings)."""
    if not history:
        return ""
    user_msgs: List[str] = []
    for msg in history[-2:]:
        if isinstance(msg, dict):
            if msg.get("role") == "user":
                user_msgs.append((msg.get("content") or "").strip())
        elif isinstance(msg, str):
            if msg.lower().startswith("user:"):
                user_msgs.append(msg.split(":", 1)[1].strip())
    return " ".join([m for m in user_msgs if m])

def reformulate_answer(question: str, context: str) -> str:
    """Reformule la réponse en utilisant Grok/Gemini avec des instructions claires."""
    global _all_llms_failed
    
    if not context or context.strip() == "":
        logger.warning("Contexte vide pour reformulation")
        return "Désolé, je n'ai pas trouvé d'information pertinente sur cette question."
    
    # Nettoyer le contexte
    context = _deduplicate_lines(context.strip())
    context = context.replace('===', '').replace('[', '').replace(']', '')
    
    # Ne PAS essayer les LLMs s'ils ont tous échoué (évite le segfault avec Gemini SDK)
    if not _all_llms_failed and (GENAI_AVAILABLE or GROK_AVAILABLE or OPENAI_AVAILABLE):
        try:
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
        except Exception as e:
            logger.debug(f"LLM reformulation failed: {e}")
    
    # Fallback intelligent : extraire le meilleur paragraphe du contexte
    logger.info("💡 Utilisation du fallback intelligent (extraction directe)")
    lines = [l.strip() for l in context.split('\n') if l.strip() and len(l.strip()) > 40]
    if lines:
        # Retourner les 3 premières lignes pertinentes avec formatage
        result = '\n\n'.join(lines[:3])
        return f"📚 D'après nos documents :\n\n{result}\n\n💡 Pour plus d'informations, contactez l'administration de l'IMT Dakar."
    return f"📚 Voici ce que j'ai trouvé :\n\n{context[:500]}\n\n💡 Pour plus d'informations, contactez l'administration."

import chainlit as cl
import uuid
from memory.redis_memory import RedisMemory
from app.mysql_data_layer import MySQLDataLayer

_memory = RedisMemory()

@cl.data_layer
def get_data_layer():
    return MySQLDataLayer.from_env()

@cl.on_chat_start
async def _on_chat_start():
    session_id = str(uuid.uuid4())
    _memory.create_session(session_id)
    cl.user_session.set("session_id", session_id)
    if not os.getenv("DATABASE_URL"):
        await cl.Message(
            content="ATTENTION: DATABASE_URL manquant. La persistance de l'historique est desactivee."
        ).send()
    await cl.Message(
        content="Bonjour ! Je suis l'assistant de l'Institut Mines-Telecom Dakar. Comment puis-je vous aider ?"
    ).send()

@cl.on_message
async def _on_message(message: cl.Message):
    user_message = message.content.strip()
    session_id = cl.user_session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        _memory.create_session(session_id)
        cl.user_session.set("session_id", session_id)

    _memory.add_message(session_id, "user", user_message)
    response = agent(user_message, memory_manager=_memory, session_id=session_id)
    _memory.add_message(session_id, "assistant", response)
    await cl.Message(content=response).send()

if __name__ == "__main__":
    print("Agent IMT prêt\n")
    while True:
        question = input("Posez votre question à l'agent IMT (ou 'quit' pour quitter) : ")
        if question.lower() == 'quit':
            break
        response = agent(question)
        print(response)
        print("\n---\n")
