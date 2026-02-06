import chainlit as cl
import os
import logging
import re
import uuid
from dotenv import load_dotenv
from app.tools import search_imt, send_email
from app.agent import reformulate_answer  # Import de la fonction Gemini
from memory.redis_memory import RedisMemory
from app.mysql_data_layer import MySQLDataLayer

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

memory = RedisMemory()


@cl.data_layer
def get_data_layer():
    return MySQLDataLayer.from_env()

def format_response(question: str, context: str) -> str:
    """Formatte une réponse simple et claire basée sur le contexte."""
    if not context or "Je n'ai pas trouvé" in context:
        return "Je n'ai pas trouvé d'information pertinente sur cette question. Pour plus de détails, contactez l'administration de l'IMT Dakar."
    
    # Nettoyer le contexte
    lines = [l.strip() for l in context.split('\n') if l.strip() and len(l.strip()) > 40]
    
    # Questions courantes avec réponses directes
    q_lower = question.lower()
    
    if any(word in q_lower for word in ['bonjour', 'salut', 'bonsoir', 'hello']):
        return "Bonjour ! Je suis l'assistant de l'Institut Mines-Télécom Dakar. Comment puis-je vous aider ?"
    
    if any(word in q_lower for word in ['formation', 'programme', 'cursus', 'diplôme']):
        info = '\n'.join(lines[:3])
        return f"L'IMT Dakar propose plusieurs formations :\n\n{info}\n\nPour plus d'informations, contactez l'administration."
    
    if any(word in q_lower for word in ['contact', 'téléphone', 'email', 'adresse', 'où', 'localisation']):
        info = '\n'.join(lines[:2])
        return f"Voici les coordonnées :\n\n{info}"
    
    # Réponse générique
    info = '\n'.join(lines[:3])
    return f"D'après nos documents :\n\n{info}\n\nPour plus de détails, contactez l'administration."

@cl.on_chat_start
async def start():
    # Créer un ID unique pour la session Redis (backend)
    session_id = str(uuid.uuid4())
    memory.create_session(session_id)
    cl.user_session.set("session_id", session_id)
    cl.user_session.set("messages", [])

    logger.info(f"🆕 Nouvelle session créée: {session_id}")
    
    # Note : Chainlit gère son propre système de threads/sidebar
    # Notre système Redis (3 sessions, TTL 1h) est indépendant mais complémentaire

    await cl.Message(
        content="Bonjour ! Je suis l'assistant de l'Institut Mines-Télécom Dakar. Comment puis-je vous aider ?"
    ).send()

@cl.on_settings_update
async def setup_agent(settings):
    """Gère les mises à jour de settings (utilisé pour le sidebar)."""
    pass

@cl.on_chat_resume
async def on_chat_resume():
    """Appelé quand Chainlit restaure un thread depuis le sidebar.
    
    Note : Chainlit gère automatiquement la restauration des messages via MySQL.
    Notre système Redis est indépendant et ne nécessite pas d'intervention ici.
    """
    logger.info("🔄 Thread Chainlit restauré depuis le sidebar UI")
    pass

@cl.on_audio_start
async def on_audio_start():
    """Appelé quand l'utilisateur commence un enregistrement vocal (STT)."""
    logger.info("🎤 Enregistrement vocal démarré")
    return True

@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.AudioChunk):
    """Reçoit les morceaux audio pendant l'enregistrement (streaming STT)."""
    # Chainlit gère automatiquement la transcription via Web Speech API
    pass

@cl.on_audio_end
async def on_audio_end(elements: list[cl.Element]):
    """Appelé quand l'enregistrement vocal se termine.
    
    Args:
        elements: Liste contenant l'audio transcrit en texte
    """
    logger.info(f"🎤 Enregistrement vocal terminé ({len(elements)} éléments reçus)")
    # Le texte transcrit est automatiquement envoyé comme message via on_message
    pass

@cl.on_message
async def main(message: cl.Message):
    user_message = message.content.strip()
    
    # Gérer les fichiers uploadés
    uploaded_files = []
    if message.elements:
        for element in message.elements:
            if hasattr(element, 'path') and element.path:
                uploaded_files.append(element)
                logger.info(f"📎 Fichier reçu: {element.name} ({element.mime})")
    
    # Extraire le contenu des fichiers uploadés
    file_contents = []
    for file_elem in uploaded_files:
        try:
            if file_elem.mime == "text/plain" or file_elem.name.endswith(".txt"):
                with open(file_elem.path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_contents.append(f"\n**Contenu de {file_elem.name}**:\n{content[:1000]}")
                    logger.info(f"✅ Contenu TXT extrait ({len(content)} caractères)")
            elif file_elem.mime == "application/pdf" or file_elem.name.endswith(".pdf"):
                # Pour les PDF, on informe l'utilisateur
                file_contents.append(f"\n📄 **Fichier PDF reçu** : {file_elem.name}")
                file_contents.append("Note : L'extraction PDF nécessite PyPDF2 (non installé actuellement).")
                logger.warning(f"⚠️ PDF reçu mais extraction non disponible: {file_elem.name}")
        except Exception as e:
            logger.error(f"❌ Erreur lecture fichier {file_elem.name}: {e}")
            file_contents.append(f"\n⚠️ Impossible de lire {file_elem.name}")
    
    # Ajouter le contenu des fichiers au message utilisateur
    if file_contents:
        user_message += "\n\n" + "\n".join(file_contents)

    session_id = cl.user_session.get("session_id")
    
    # Commande pour afficher l'historique des sessions
    if user_message.lower() in ["historique", "mes discussions", "sessions", "liste sessions"]:
        sessions = memory.list_sessions()
        current_session = cl.user_session.get("session_id")
        
        response = "## 📊 Sessions actives (Backend Redis)\n\n"
        response += f"**Limite** : {memory.MAX_SESSIONS} sessions simultanées\n"
        response += f"**TTL** : {memory.SESSION_TTL // 60} minutes\n\n"
        
        if not sessions:
            response += "*Aucune session active pour le moment.*"
        else:
            for i, sess in enumerate(sessions, 1):
                sess_id = sess.get("session_id", "N/A")
                is_current = "✅ **Actuelle**" if sess_id == current_session else ""
                msg_count = sess.get("message_count", 0)
                ttl_min = sess.get("ttl_remaining", 0) // 60
                
                response += f"### Session {i} {is_current}\n"
                response += f"- **ID** : `{sess_id[:12]}...`\n"
                response += f"- **Messages** : {msg_count}\n"
                response += f"- **Expire dans** : {ttl_min} min\n\n"
        
        response += "\n---\n\n"
        response += "💡 **Note** : Chainlit UI gère également son propre historique dans le sidebar (si disponible)."
        
        await cl.Message(content=response).send()
        return
    
    # Stocker le message dans la session Chainlit
    messages = cl.user_session.get("messages")
    if messages is None:
        messages = []
        cl.user_session.set("messages", messages)
    messages.append({"role": "user", "content": user_message})

    # Ajout Redis
    if session_id:
        memory.add_message(session_id, "user", user_message)
    
    # Détecter si c'est une demande d'email
    query_lower = user_message.lower()
    email_keywords = ["email", "envoyer", "envoie", "ecris", "contacter"]
    
    if any(kw in query_lower for kw in email_keywords) and "comment" not in query_lower:
        response = send_email(
            subject="Demande d'informations",
            content=f"Message de l'utilisateur:\n\n{user_message}",
            recipient=os.getenv("EMAIL_TO", "contact@imt.sn")
        )
    else:
        # Rechercher le contexte
        context = search_imt(user_message)
        
        # Utiliser Gemini pour générer une réponse intelligente
        logger.info("🤖 Utilisation de Gemini 2.5 Flash pour la réponse...")
        response = reformulate_answer(user_message, context)
        
        # Fallback si Gemini échoue
        if not response or response == context:
            response = format_response(user_message, context)
    
    # Stocker la réponse
    messages.append({"role": "assistant", "content": response})

    # Ajout Redis
    if session_id:
        memory.add_message(session_id, "assistant", response)
    
    # Créer un bouton TTS (Text-to-Speech) sur le message
    actions = [
        cl.Action(name="tts", value="speak", label="🔊 Écouter", description="Lire ce message à voix haute")
    ]
    
    await cl.Message(content=response, actions=actions).send()

@cl.action_callback("tts")
async def on_tts_action(action: cl.Action):
    """Callback pour le bouton TTS - lit le message à voix haute."""
    # Le message parent contient le texte à lire
    msg = action.value
    
    # Envoyer un message audio (nécessite que le navigateur supporte Web Speech API)
    await cl.Message(
        content="🔊 **Lecture audio en cours...**\n\nVeuillez activer le son de votre navigateur.",
        author="System"
    ).send()
    
    # Note : Le vrai TTS nécessite une intégration avec une API externe (Google TTS, ElevenLabs, etc.)
    # Chainlit ne fournit pas de TTS natif côté serveur
    logger.info("🔊 Bouton TTS cliqué (TTS backend non implémenté)")
