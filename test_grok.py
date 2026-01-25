#!/usr/bin/env python3
from app.agent import agent
from memory.redis_memory import RedisMemory

memory = RedisMemory()
session_id = 'test_grok'

print('=== TEST GROK ===')
q = "C'est quoi l'IMT Dakar ?"
print(f'Question: {q}')
r = agent(q, memory_manager=memory, session_id=session_id)
print(f'Réponse: {r}')
