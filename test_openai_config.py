#!/usr/bin/env python3
"""
Test de configuration OpenAI pour l'agent IMT
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Vérification de la configuration OpenAI\n")
print("=" * 60)

# Vérifier la présence de la clé
openai_key = os.getenv("OPENAI_API_KEY")

if not openai_key or openai_key.strip() == "":
    print("❌ OPENAI_API_KEY n'est pas configurée dans .env\n")
    print("📝 Pour configurer OpenAI :")
    print("   1. Créer un compte sur https://platform.openai.com")
    print("   2. Ajouter 5$ de crédits (minimum OpenAI)")
    print("   3. Générer une clé API sur https://platform.openai.com/api-keys")
    print("   4. Ajouter dans .env : OPENAI_API_KEY=sk-proj-XXXXX")
    print("\n💡 Voir le guide complet : docs/GUIDE_OPENAI.md")
    print("\n⚠️  En attendant, l'agent utilisera le fallback (pas de reformulation LLM)")
else:
    print(f"✅ OPENAI_API_KEY configurée : {openai_key[:20]}...{openai_key[-4:]}")
    
    # Tester la connexion
    print("\n🧪 Test de connexion à OpenAI...\n")
    
    try:
        import openai
        client = openai.OpenAI(api_key=openai_key)
        
        # Test simple
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Dis juste 'OK' si tu fonctionnes"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI fonctionne ! Réponse : {result}")
        print(f"📊 Tokens utilisés : {response.usage.total_tokens}")
        print(f"💰 Coût estimé : ~${response.usage.total_tokens * 0.0000006:.6f}")
        
    except openai.AuthenticationError:
        print("❌ Clé API invalide")
        print("   Vérifie que tu as bien copié la clé complète depuis")
        print("   https://platform.openai.com/api-keys")
    except openai.RateLimitError:
        print("❌ Limite de requêtes atteinte")
        print("   Attends 1-2 minutes avant de réessayer")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        print("   Vérifie ton compte OpenAI sur https://platform.openai.com")

print("\n" + "=" * 60)
print("\n💡 Ordre de priorité de l'agent IMT :")
print("   1. Grok (xAI)")
print("   2. OpenAI GPT-4o-mini ✨")
print("   3. Gemini (Google)")
print("   4. Fallback (sans reformulation)")
