#!/usr/bin/env python3
"""Test rapide de Gemini"""
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
print(f"🔑 Clé API: {API_KEY[:20]}...")

client = genai.Client(api_key=API_KEY)

prompt = "Réponds en une phrase courte : Bonjour, comment ça va ?"

try:
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=100,
        )
    )
    print(f"\n✅ Réponse Gemini: {response.text}\n")
except Exception as e:
    print(f"\n❌ Erreur: {e}\n")
