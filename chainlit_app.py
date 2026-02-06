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
    # Créer un ID unique pour la session Redis
    session_id = str(uuid.uuid4())
    memory.create_session(session_id)
    cl.user_session.set("session_id", session_id)
    cl.user_session.set("messages", [])

    logger.info(f"🆕 Nouvelle session créée: {session_id}")
    
    # Le thread Chainlit est créé automatiquement par le data layer
    # On récupère son ID via cl.context.session
    thread_id = cl.context.session.id if cl.context.session else session_id
    logger.info(f"📝 Thread Chainlit ID: {thread_id}")

    await cl.Message(
        content="Bonjour ! Je suis l'assistant de l'Institut Mines-Télécom Dakar. Comment puis-je vous aider ?"
    ).send()

@cl.on_settings_update
async def setup_agent(settings):
    """Gère les mises à jour de settings (utilisé pour le sidebar)."""
    pass

@cl.on_chat_resume
async def on_chat_resume():
    """Appelé quand une session est restaurée."""
    pass

@cl.on_message
async def main(message: cl.Message):
    user_message = message.content.strip()

    session_id = cl.user_session.get("session_id")
    
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
    
    await cl.Message(content=response).send()
