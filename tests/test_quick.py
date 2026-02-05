#!/usr/bin/env python3
"""Test rapide de l'agent."""
import os

# FORCER la désactivation de Gemini pour éviter segfault
os.environ.pop('GEMINI_API_KEY', None)
os.environ.pop('GOOGLE_API_KEY', None)

# Importer APRÈS avoir nettoyé l'environnement
import app.agent as agent_module
agent_module.GENAI_AVAILABLE = False  # Force disable
agent_module.GROK_AVAILABLE = False   # Quotas épuisés aussi
agent_module.OPENAI_AVAILABLE = False # Quotas épuisés aussi

from app.agent import agent

print("=" * 50)
print("TEST AGENT (fallback pur - pas de LLM)")
print("=" * 50)
response = agent("C'est quoi l'IMT Dakar ?")
print("\n📝 RÉPONSE:")
print(response)
print("\n" + "=" * 50)
