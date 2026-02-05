#!/usr/bin/env python3
"""Test des corrections : profil et extraction email"""
from app.agent import agent, _extract_personal_info
from memory.redis_memory import RedisMemory

# Test extraction profil
print("=" * 60)
print("🧪 TEST EXTRACTION INFOS PERSONNELLES")
print("=" * 60)

test_phrases = [
    "je suis un jeune homme",
    "je suis une étudiante",
    "je suis un développeur",
    "Je m'appelle Maliki",
    "mon email est test@example.com",
]

for phrase in test_phrases:
    entities = _extract_personal_info(phrase)
    print(f"\n📝 '{phrase}'")
    if entities:
        for key, val in entities.items():
            print(f"   → {key}: {val}")
    else:
        print("   → Rien détecté")

print("\n" + "=" * 60)
print("🧪 TEST AGENT COMPLET AVEC PROFIL")
print("=" * 60)

memory = RedisMemory()
session_id = 'test_profile_session'
memory.clear_history(session_id)

# Test 1: Enregistrer profil
print("\n📝 TEST 1: je suis un jeune homme")
q1 = "je suis un jeune homme"
r1 = agent(q1, memory_manager=memory, session_id=session_id)
print(f"Réponse: {r1}")

# Test 2: Enregistrer nom
print("\n📝 TEST 2: Je m'appelle Maliki")
q2 = "Je m'appelle Maliki"
r2 = agent(q2, memory_manager=memory, session_id=session_id)
print(f"Réponse: {r2}")

# Test 3: Rappeler
print("\n📝 TEST 3: Qui suis-je ?")
q3 = "Qui suis-je ?"
r3 = agent(q3, memory_manager=memory, session_id=session_id)
print(f"Réponse: {r3}")

print("\n💾 Entités stockées:")
entities = memory.get_all_entities(session_id)
for k, v in entities.items():
    print(f"  - {k}: {v}")

print("\n" + "=" * 60)
print("✅ TESTS TERMINÉS")
print("=" * 60)
