#!/usr/bin/env python3
"""Test des corrections de l'agent"""
from app.agent import agent

print("=== TEST 1 : Email avec extraction ===")
r1 = agent('envoie un mail avec message "Test correction extraction"')
print(r1[:200])
print()

print("=== TEST 2 : Question identitaire ===")
r2 = agent("C'est quoi l'IMT Dakar ?")
print(r2)
print()

print("=== TEST 3 : Formations (déduplication) ===")
r3 = agent("Quelles formations propose l'IMT ?")
print(r3[:300])
