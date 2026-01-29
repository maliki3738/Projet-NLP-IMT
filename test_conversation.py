#!/usr/bin/env python3
"""Test conversationnel de l'agent IMT - simule une vraie conversation."""

import sys
sys.path.insert(0, '/Users/mac/Desktop/NLP/Projet/imt-agent-clean')

from app.agent import agent

print("="*60)
print("TEST AGENT IMT - Conversation Simulée")
print("="*60)

questions = [
    "C'est quoi l'IMT Dakar ?",
    "Où est-ce situé ?",
    "Quelles formations proposent-ils ?",
    "Comment les contacter ?"
]

for i, q in enumerate(questions, 1):
    print(f"\n[Q{i}] {q}")
    print("-" * 60)
    response = agent(q)
    print(response[:400] + "..." if len(response) > 400 else response)
    print()

print("="*60)
print("✅ Test conversationnel terminé")
print("="*60)
