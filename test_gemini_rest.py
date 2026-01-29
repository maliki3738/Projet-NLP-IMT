#!/usr/bin/env python3
"""Test Gemini avec API REST"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
print(f"🔑 Clé API: {API_KEY[:20]}...")

url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={API_KEY}"

payload = {
    "contents": [{
        "parts": [{"text": "Réponds en une phrase courte : Bonjour, comment ça va ?"}]
    }],
    "generationConfig": {
        "temperature": 0.3,
        "maxOutputTokens": 100,
    }
}

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"\n📡 Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        text = data['candidates'][0]['content']['parts'][0]['text']
        print(f"✅ Réponse: {text}\n")
    else:
        print(f"❌ Erreur: {response.text[:300]}\n")
except Exception as e:
    print(f"\n❌ Exception: {e}\n")
