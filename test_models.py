#!/usr/bin/env python3
"""Test des modèles Gemini compatibles avec LangChain"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# S'assurer que la clé API est définie
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY', 'AIzaSyDTVSrsUfylRKmUnU40Q9fCadDKmYePcLY')

models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-pro", 
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]

print("=" * 60)
print("Test des modèles Gemini avec LangChain")
print("=" * 60)

for model_name in models_to_test:
    try:
        print(f"\n🧪 Test: {model_name}")
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.2)
        result = llm.invoke("Dis bonjour en français en une phrase courte")
        print(f"✅ RÉUSSI: {result.content[:80]}")
        break  # Si ça marche, on arrête
    except Exception as e:
        error_msg = str(e)
        if "NOT_FOUND" in error_msg:
            print(f"❌ Modèle non trouvé")
        elif "API key" in error_msg:
            print(f"❌ Problème de clé API")
        else:
            print(f"❌ Erreur: {error_msg[:100]}")

print("\n" + "=" * 60)
