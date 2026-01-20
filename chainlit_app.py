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
    Loads conversation history from memory (Redis or RAM).
    """
    # Get session ID - try different ways for compatibility
    try:
        session_id = cl.user_session.get("id") or cl.user_session.get("session_id") or "default"
    except:
        session_id = "default"

    # Load history if exists and replay previous messages
    history = memory.get_history(session_id)
    if history:
        # Send history messages to restore conversation context
        for msg in history:
            if msg.startswith("user: "):
                await cl.Message(author="user", content=msg[6:]).send()
            elif msg.startswith("assistant: "):
                await cl.Message(author="assistant", content=msg[11:]).send()

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

    # Store user message in memory
    memory.add_message(session_id, "user", message.content)

    # Call the IMT agent (handles search vs email decisions)
    response = agent(message.content)

    # Store assistant response in memory
    memory.add_message(session_id, "assistant", response)

    # Send response to user
    await cl.Message(content=response).send()