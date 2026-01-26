import chainlit as cl
import os
from dotenv import load_dotenv

# Import des deux agents : ancien et nouveau (LangChain)
from app.agent import agent as old_agent
# TEMPORAIRE: LangChain agent désactivé (API breaking changes v1.x)
# from app.langchain_agent import create_imt_agent, run_agent
from memory.redis_memory import RedisMemory

load_dotenv()

# Configuration : choisir quel agent utiliser  
# FORCE OLD AGENT (LangChain needs update)
USE_LANGCHAIN = False  # os.getenv("USE_LANGCHAIN_AGENT", "true").lower() == "true"

# Initialize Redis memory with fallback to RAM if Redis unavailable
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
memory = RedisMemory(host=redis_host, port=redis_port)

# Agent LangChain global (créé une seule fois)
langchain_agent = None

@cl.on_chat_start
async def start():
    """
    Called when a new chat session starts.
    Initializes the LangChain agent if enabled.
    """
    global langchain_agent
    
    # Créer l'agent LangChain si activé et pas encore créé
    if USE_LANGCHAIN and langchain_agent is None:
        try:
            # langchain_agent = create_imt_agent(verbose=False)  # DISABLED
            await cl.Message(
                content="🤖 Agent IMT LangChain initialisé avec succès !\n\n"
                        "Posez-moi vos questions sur l'IMT ou demandez-moi d'envoyer un email."
            ).send()
        except ValueError as e:
            await cl.Message(
                content=f"⚠️ Impossible d'initialiser l'agent LangChain : {e}\n"
                        "Utilisation de l'agent classique à la place."
            ).send()
    elif not USE_LANGCHAIN:
        await cl.Message(
            content="🤖 Agent IMT classique activé.\n\n"
                    "Posez-moi vos questions sur l'IMT !"
        ).send()

@cl.on_message
async def main(message: cl.Message):
    """
    Main message handler - called for each user message.
    Processes the message through the agent and stores conversation.
    """
    try:
        session_id = cl.user_session.get("id") or cl.user_session.get("session_id") or "default"
    except:
        session_id = "default"

    # Special command to show full history
    if message.content.lower().strip() == "/historique" or message.content.lower().strip() == "/history":
        if memory:
            history = memory.get_history(session_id)
            if history:
                history_text = "**📜 Historique complet de la conversation :**\n\n"
                for i, msg in enumerate(history, 1):
                    if msg.startswith("user: "):
                        history_text += f"**Vous {i//2 + 1}:** {msg[6:]}\n"
                    elif msg.startswith("assistant: "):
                        history_text += f"**Agent {i//2 + 1}:** {msg[11:]}\n"
                await cl.Message(content=history_text).send()
            else:
                await cl.Message(content="Aucun historique trouvé pour cette session.").send()
        else:
            await cl.Message(content="⚠️ La mémoire Redis est désactivée. Historique non disponible.").send()
        return

    # Store user message in memory
    if memory:
        memory.add_message(session_id, "user", message.content)

    # Get conversation history for context
    history = memory.get_history(session_id) if memory else []

    # Choisir quel agent utiliser
    if USE_LANGCHAIN and langchain_agent is not None:
        # Utiliser l'agent LangChain (DISABLED)
        # response = run_agent(message.content, agent=langchain_agent)
        response = "❌ LangChain agent temporairement désactivé (API v1.x breaking changes)"
    else:
        # Utiliser l'agent classique avec historique et mémoire
        response = old_agent(message.content, history=history, memory_manager=memory, session_id=session_id)

    # Store assistant response in memory
    if memory:
        memory.add_message(session_id, "assistant", response)

    # Send response to user
    await cl.Message(content=response).send()