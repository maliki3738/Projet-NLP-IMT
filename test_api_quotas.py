#!/usr/bin/env python3
"""
Vérifie l'état des quotas API (Grok, OpenAI, Gemini).
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("📊 ÉTAT DES QUOTAS API")
print("=" * 80)

# Vérifier Grok
print("\n🤖 GROK (xAI)")
grok_key = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
if grok_key:
    print(f"   ✅ Clé configurée : {grok_key[:15]}...")
    try:
        import openai
        client = openai.OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        print("   ✅ QUOTA OK : Grok répond normalement")
    except Exception as e:
        if "429" in str(e):
            print("   ❌ QUOTA ÉPUISÉ : Crédits insuffisants")
            print(f"   ℹ️  Erreur : {str(e)[:100]}")
        else:
            print(f"   ⚠️  Erreur : {e}")
else:
    print("   ⚠️  Clé non configurée")

# Vérifier OpenAI
print("\n🤖 OPENAI GPT")
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    print(f"   ✅ Clé configurée : {openai_key[:15]}...")
    try:
        import openai
        client = openai.OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        print("   ✅ QUOTA OK : OpenAI répond normalement")
    except Exception as e:
        if "insufficient_quota" in str(e):
            print("   ❌ QUOTA ÉPUISÉ : Besoin de 5$ crédits minimum")
            print("   💰 Achat : https://platform.openai.com/settings/organization/billing")
        elif "429" in str(e):
            print("   ❌ QUOTA ÉPUISÉ : Limite atteinte")
        else:
            print(f"   ⚠️  Erreur : {e}")
else:
    print("   ⚠️  Clé non configurée")

# Vérifier Gemini
print("\n🤖 GEMINI")
gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if gemini_key:
    print(f"   ✅ Clé configurée : {gemini_key[:15]}...")
    try:
        from google import genai
        client = genai.Client(api_key=gemini_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="test"
        )
        print("   ✅ QUOTA OK : Gemini répond normalement")
    except Exception as e:
        error_str = str(e)
        if "429" in error_str and "RESOURCE_EXHAUSTED" in error_str:
            # Extraire le temps de retry
            import re
            retry_match = re.search(r'retry in (\d+(?:\.\d+)?)s', error_str)
            if retry_match:
                retry_seconds = float(retry_match.group(1))
                retry_minutes = retry_seconds / 60
                print(f"   ❌ QUOTA ÉPUISÉ (Free Tier)")
                print(f"   ⏰ Disponible dans : {retry_minutes:.1f} minutes ({retry_seconds:.0f}s)")
                
                # Calcul de l'heure de disponibilité
                from datetime import datetime, timedelta
                now = datetime.now()
                available_at = now + timedelta(seconds=retry_seconds)
                print(f"   🕐 Heure disponibilité : {available_at.strftime('%H:%M:%S')}")
            else:
                print("   ❌ QUOTA ÉPUISÉ (Free Tier)")
            
            # Vérifier si quota quotidien
            if "GenerateRequestsPerDayPerProjectPerModel" in error_str:
                print("   📅 Type : QUOTA QUOTIDIEN - Réinitialisation minuit UTC")
        else:
            print(f"   ⚠️  Erreur : {e}")
else:
    print("   ⚠️  Clé non configurée")

print("\n" + "=" * 80)
print("💡 RECOMMANDATIONS")
print("=" * 80)
print("\n✅ Tests sans LLM disponibles :")
print("   • python test_rag_only.py      (RAG vectoriel seul)")
print("   • python test_tools_only.py    (Outils search + email)")
print("   • python test_personal_memory.py (Mémoire Redis)")
print("\n💰 Pour activer les LLM :")
print("   • OpenAI : Acheter 5$ crédits (0.04-0.32$/semaine usage réel)")
print("   • Gemini : Attendre réinitialisation quota (minuit UTC)")
print("   • Grok : Recharger crédits sur x.ai")
