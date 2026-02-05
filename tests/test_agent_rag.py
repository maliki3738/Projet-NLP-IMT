#!/usr/bin/env python3
"""Test complet de l'agent avec le nouveau RAG vectoriel."""
from app.agent import agent

# Questions de test
test_questions = [
    "Quelles formations proposez-vous ?",
    "Comment vous contacter ?",
    "C'est quoi l'IMT ?",
    "Parlez-moi du bachelor en cybersécurité",
    "Quels sont les débouchés ?"
]

print("=" * 80)
print("🧪 TEST AGENT AVEC RAG VECTORIEL")
print("=" * 80)

for i, question in enumerate(test_questions, 1):
    print(f"\n{'='*80}")
    print(f"📌 Question {i}: {question}")
    print(f"{'='*80}")
    
    response = agent(question)
    print(f"\n🤖 Réponse:\n{response}\n")
