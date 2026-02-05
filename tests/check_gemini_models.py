#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
print(f"Clé: {key[:20]}...")

# Test v1beta
print("\n" + "="*60)
print("TEST API v1beta")
print("="*60)
url_beta = f'https://generativelanguage.googleapis.com/v1beta/models?key={key}'
resp_beta = requests.get(url_beta, timeout=10)
print(f"Status: {resp_beta.status_code}")

if resp_beta.status_code == 200:
    models = resp_beta.json().get('models', [])
    print(f"✅ Nombre de modèles: {len(models)}\n")
    print("Modèles supportant generateContent:")
    for m in models:
        name = m.get('name', 'N/A').replace('models/', '')
        methods = m.get('supportedGenerationMethods', [])
        if 'generateContent' in methods:
            print(f"  ✅ {name}")
else:
    print(f"❌ Erreur: {resp_beta.text[:300]}")

# Test simple avec un modèle
print("\n" + "="*60)
print("TEST generateContent avec gemini-pro")
print("="*60)

test_models = ['gemini-pro', 'gemini-1.5-flash', 'gemini-1.5-pro']
for model_name in test_models:
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}'
    payload = {
        "contents": [{"parts": [{"text": "Bonjour"}]}],
        "generationConfig": {"maxOutputTokens": 10}
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            print(f"  ✅ {model_name} : FONCTIONNE")
        elif resp.status_code == 429:
            print(f"  ⚠️  {model_name} : QUOTA ÉPUISÉ")
        elif resp.status_code == 404:
            print(f"  ❌ {model_name} : N'EXISTE PAS")
        else:
            print(f"  ❌ {model_name} : Erreur {resp.status_code}")
    except Exception as e:
        print(f"  ❌ {model_name} : {str(e)[:50]}")
