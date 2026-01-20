import chainlit as cl
from app.agent import agent
from memory.redis_memory import RedisMemory
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Redis memory with fallback to RAM if Redis unavailable
# This allows the app to work even without Redis installed
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
memory = RedisMemory(host=redis_host, port=redis_port)

@cl.on_chat_start
async def start():
    """
    Called when a new chat session starts.
    Chainlit handles message persistence automatically, so we don't need to manually reload history.
    The memory is used for long-term persistence across sessions if needed.
    """
    # Session initialization - Chainlit handles message history automatically
    # The RedisMemory is used for cross-session persistence if Redis is available
    pass

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
        return

    # Store user message in memory
    memory.add_message(session_id, "user", message.content)

    # Call the IMT agent (handles search vs email decisions)
    response = agent(message.content)

    # Store assistant response in memory
    memory.add_message(session_id, "assistant", response)

    # Send response to user
    await cl.Message(content=response).send()