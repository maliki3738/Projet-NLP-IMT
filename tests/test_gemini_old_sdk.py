#!/usr/bin/env python3
"""Test Gemini avec l'ancien SDK"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
print(f"🔑 Clé API: {API_KEY[:20]}...")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

prompt = "Réponds en une phrase courte : Bonjour, comment ça va ?"

try:
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.3,
            max_output_tokens=100,
        )
    )
    print(f"\n✅ Réponse Gemini: {response.text}\n")
except Exception as e:
    print(f"\n❌ Erreur: {e}\n")
