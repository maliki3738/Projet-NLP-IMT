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
    session_id = str(uuid.uuid4())
    memory.create_session(session_id)
    cl.user_session.set("session_id", session_id)
    cl.user_session.set("messages", [])

    logger.info(f"🆕 Nouvelle session créée: {session_id}")

    # Afficher les sessions actives dans l'interface
    sessions = memory.list_sessions()
    
    # Créer un affichage HTML des sessions
    sessions_html = """
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 12px; 
                padding: 20px; 
                margin: 10px 0; 
                color: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3 style="margin: 0 0 15px 0; font-size: 18px; display: flex; align-items: center;">
            <span style="margin-right: 8px;">💬</span> Sessions Actives ({}/3)
        </h3>
    """.format(len(sessions))
    
    if sessions:
        for i, sess in enumerate(sessions, 1):
            is_current = sess['session_id'] == session_id
            ttl_min = sess['ttl_remaining'] // 60
            status_icon = "🟢" if is_current else "⚪"
            border = "2px solid #ffd700" if is_current else "1px solid rgba(255,255,255,0.3)"
            
            sessions_html += f"""
            <div style="background: rgba(255,255,255,0.1); 
                        border: {border}; 
                        border-radius: 8px; 
                        padding: 12px; 
                        margin: 8px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-weight: bold;">{status_icon} Session {i}</span>
                        {' (Actuelle)' if is_current else ''}
                    </div>
                    <div style="font-size: 12px; opacity: 0.9;">
                        ⏱️ {ttl_min} min restantes
                    </div>
                </div>
                <div style="font-size: 12px; margin-top: 5px; opacity: 0.8;">
                    💬 {sess['message_count']} messages
                </div>
            </div>
            """
    else:
        sessions_html += """
        <p style="text-align: center; opacity: 0.8; margin: 10px 0;">
            Aucune session active
        </p>
        """
    
    sessions_html += """
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); 
                    font-size: 12px; opacity: 0.8;">
            ℹ️ Maximum 3 sessions simultanées • 1h de validité • Suppression auto de la plus ancienne
        </div>
    </div>
    """
    
    # Envoyer le widget des sessions
    await cl.Message(
        content=sessions_html,
        author="System"
    ).send()
    
    # Message de bienvenue
    await cl.Message(
        content="Bonjour ! Je suis l'assistant de l'Institut Mines-Télécom Dakar. Comment puis-je vous aider ?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    user_message = message.content.strip()

    session_id = cl.user_session.get("session_id")
    
    # Commande spéciale : afficher les sessions
    if user_message.lower() in ['/sessions', '/status', '/info']:
        sessions = memory.list_sessions()
        
        sessions_html = """
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 12px; 
                    padding: 20px; 
                    margin: 10px 0; 
                    color: white;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 15px 0; font-size: 18px; display: flex; align-items: center;">
                <span style="margin-right: 8px;">💬</span> Sessions Actives ({}/3)
            </h3>
        """.format(len(sessions))
        
        if sessions:
            for i, sess in enumerate(sessions, 1):
                is_current = sess['session_id'] == session_id
                ttl_min = sess['ttl_remaining'] // 60
                status_icon = "🟢" if is_current else "⚪"
                border = "2px solid #ffd700" if is_current else "1px solid rgba(255,255,255,0.3)"
                
                sessions_html += f"""
                <div style="background: rgba(255,255,255,0.1); 
                            border: {border}; 
                            border-radius: 8px; 
                            padding: 12px; 
                            margin: 8px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-weight: bold;">{status_icon} Session {i}</span>
                            {' (Actuelle)' if is_current else ''}
                        </div>
                        <div style="font-size: 12px; opacity: 0.9;">
                            ⏱️ {ttl_min} min restantes
                        </div>
                    </div>
                    <div style="font-size: 12px; margin-top: 5px; opacity: 0.8;">
                        💬 {sess['message_count']} messages
                    </div>
                </div>
                """
        
        sessions_html += """
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); 
                        font-size: 12px; opacity: 0.8;">
                💡 Tapez /sessions pour voir ce panneau à tout moment
            </div>
        </div>
        """
        
        await cl.Message(content=sessions_html, author="System").send()
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
    
    await cl.Message(content=response).send()
