#!/usr/bin/env python3
"""Test simple de l'agent LangChain sans Chainlit"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY', 'AIzaSyDTVSrsUfylRKmUnU40Q9fCadDKmYePcLY')

from app.langchain_agent import create_imt_agent, run_agent

print("=" * 60)
print("TEST DE L'AGENT LANGCHAIN (sans Chainlit)")
print("=" * 60)

# Créer l'agent
print("\n🔧 Création de l'agent...")
agent = create_imt_agent()
print("✅ Agent créé !")

# Test 1: Question simple
print("\n" + "=" * 60)
print("TEST 1: Question simple sur l'IMT")
print("=" * 60)
question1 = "C'est quoi l'IMT Dakar ?"
print(f"\n❓ Question: {question1}")
print("\n💭 Réponse:")
result1 = run_agent(agent, question1)
print(result1)

print("\n" + "=" * 60)
print("✅ TEST TERMINÉ !")
print("=" * 60)
