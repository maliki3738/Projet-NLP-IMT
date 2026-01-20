import chainlit as cl
from app.agent import agent
from memory.redis_memory import RedisMemory
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Redis memory
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
memory = RedisMemory(host=redis_host, port=redis_port)

@cl.on_chat_start
async def start():
    # Get session ID
    session_id = cl.user_session.get("id")
    # Load history if exists
    history = memory.get_history(session_id)
    if history:
        # Send history messages
        for msg in history:
            if msg.startswith("user: "):
                await cl.Message(author="user", content=msg[6:]).send()
            elif msg.startswith("assistant: "):
                await cl.Message(author="assistant", content=msg[11:]).send()

@cl.on_message
async def main(message: cl.Message):
    session_id = cl.user_session.get("id")

    # Add user message to memory
    memory.add_message(session_id, "user", message.content)

    # Call the agent
    response = agent(message.content)

    # Add assistant response to memory
    memory.add_message(session_id, "assistant", response)

    # Send response
    await cl.Message(content=response).send()