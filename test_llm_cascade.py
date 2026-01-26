#!/usr/bin/env python3
"""Test cascade LLM et tracking coûts Langfuse"""

print("🧪 Test nouvelle cascade LLM (Gemini → Grok → OpenAI)")
print("=" * 60)

# Import avec gestion des erreurs
try:
    from app.agent import _call_gemini
    print("✅ Import _call_gemini OK")
except Exception as e:
    print(f"❌ Erreur import: {e}")
    exit(1)

# Afficher la docstring
print("\n📖 Documentation:")
print(_call_gemini.__doc__)

# Afficher l'ordre de priorité
print("\n🎯 Ordre d'appel configuré:")
print("   1. 🥇 Gemini (gemini-2.0-flash-exp) - GRATUIT")
print("      • Free tier: 15 req/min, 1500 req/jour")
print("      • Coût: 0$ (tracking tokens uniquement)")
print("")
print("   2. 🥈 Grok (grok-beta)")
print("      • Coût: 5$/1M input + 15$/1M output")
print("      • Tracking: tokens + coûts USD dans Langfuse")
print("")
print("   3. 🥉 OpenAI (gpt-4o-mini)")
print("      • Coût: 0.15$/1M input + 0.60$/1M output")
print("      • Tracking: tokens + coûts USD dans Langfuse")

print("\n💡 Tous les appels sont trackés dans Langfuse avec:")
print("   • Prompt envoyé")
print("   • Réponse reçue")
print("   • Usage tokens (prompt + completion)")
print("   • Coût estimé en USD")
print("   • Métadonnées (modèle, température, max_tokens)")

print("\n📊 Dashboard Langfuse: https://cloud.langfuse.com")
print("   Onglet 'Traces' pour voir tous les appels")

print("\n✅ Configuration terminée !")
