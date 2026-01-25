#!/usr/bin/env python3
"""Test de la mémoire personnelle"""
from app.agent import agent
from memory.redis_memory import RedisMemory

# Créer une session de test
memory = RedisMemory()
session_id = 'test_personal_memory'
memory.clear_history(session_id)

print("=" * 60)
print("🧪 TEST DE MÉMOIRE PERSONNELLE")
print("=" * 60)

# Test 1: Enregistrer un nom
print("\n📝 TEST 1: Je retiens que je m'appelle Maliki")
q1 = "Je retiens que je m'appelle Maliki"
memory.add_message(session_id, 'user', q1)
r1 = agent(q1, history=memory.get_history(session_id), memory_manager=memory, session_id=session_id)
memory.add_message(session_id, 'assistant', r1)
print(f"Question: {q1}")
print(f"Réponse: {r1}\n")

# Test 2: Rappeler le nom
print("🔍 TEST 2: Je m'appelle comment ?")
q2 = "Je m'appelle comment ?"
memory.add_message(session_id, 'user', q2)
r2 = agent(q2, history=memory.get_history(session_id), memory_manager=memory, session_id=session_id)
memory.add_message(session_id, 'assistant', r2)
print(f"Question: {q2}")
print(f"Réponse: {r2}\n")

# Test 3: Variante de question
print("🔍 TEST 3: Comment je m'appelle ?")
q3 = "Comment je m'appelle ?"
memory.add_message(session_id, 'user', q3)
r3 = agent(q3, history=memory.get_history(session_id), memory_manager=memory, session_id=session_id)
memory.add_message(session_id, 'assistant', r3)
print(f"Question: {q3}")
print(f"Réponse: {r3}\n")

# Test 4: Autre variante
print("🔍 TEST 4: Mon nom c'est quoi ?")
q4 = "Mon nom c'est quoi ?"
memory.add_message(session_id, 'user', q4)
r4 = agent(q4, history=memory.get_history(session_id), memory_manager=memory, session_id=session_id)
memory.add_message(session_id, 'assistant', r4)
print(f"Question: {q4}")
print(f"Réponse: {r4}\n")

# Test 5: Question normale IMT (vérifier que ça fonctionne toujours)
print("📚 TEST 5: Question normale - Où se trouve l'IMT ?")
q5 = "Où se trouve l'IMT Dakar ?"
memory.add_message(session_id, 'user', q5)
r5 = agent(q5, history=memory.get_history(session_id), memory_manager=memory, session_id=session_id)
memory.add_message(session_id, 'assistant', r5)
print(f"Question: {q5}")
print(f"Réponse: {r5}\n")

print("=" * 60)
print("✅ TESTS TERMINÉS")
print("=" * 60)

# Afficher les entités stockées
print("\n💾 ENTITÉS STOCKÉES:")
entities = memory.get_all_entities(session_id)
for key, value in entities.items():
    print(f"  - {key}: {value}")
