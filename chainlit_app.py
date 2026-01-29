import chainlit as cl
import os
import logging
import re
from dotenv import load_dotenv
from app.tools import search_imt, send_email

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    # Initialiser la session Chainlit
    cl.user_session.set("messages", [])
    
    await cl.Message(
        content="Bonjour ! Je suis l'assistant de l'Institut Mines-Télécom Dakar. Comment puis-je vous aider ?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    user_message = message.content.strip()
    
    # Stocker le message dans la session Chainlit
    messages = cl.user_session.get("messages")
    messages.append({"role": "user", "content": user_message})
    
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
        
        # Formater une réponse simple et claire
        response = format_response(user_message, context)
    
    # Stocker la réponse
    messages.append({"role": "assistant", "content": response})
    
    await cl.Message(content=response).send()
