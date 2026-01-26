#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import re

load_dotenv()

print("=" * 80)
print("📊 VÉRIFICATION QUOTA GEMINI")
print("=" * 80)

gemini_key = os.getenv('GEMINI_API_KEY')
print(f"\n🔑 Clé: {gemini_key[:20]}..." if gemini_key else "❌ Pas de clé")

try:
    from google import genai
    client = genai.Client(api_key=gemini_key)
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp', 
        contents='test'
    )
    print('✅ QUOTA OK - Gemini répond normalement')
except Exception as e:
    error = str(e)
    if '429' in error:
        print('❌ QUOTA ÉPUISÉ')
        
        # Extraire temps de retry
        retry_match = re.search(r'retry in ([\d.]+)s', error)
        if retry_match:
            seconds = float(retry_match.group(1))
            minutes = seconds / 60
            hours = minutes / 60
            
            print(f'\n⏰ Temps restant: {minutes:.1f} minutes ({seconds:.0f}s)')
            
            now = datetime.now()
            available = now + timedelta(seconds=seconds)
            print(f'🕐 Disponible à: {available.strftime("%H:%M:%S")}')
        
        # Type de quota
        if 'PerDay' in error:
            print('\n📅 Type: QUOTA QUOTIDIEN')
            print('   Réinitialisation: Minuit UTC (01h Paris hiver, 02h été)')
        elif 'PerMinute' in error:
            print('\n📅 Type: QUOTA PAR MINUTE')
        
        print(f'\n📖 Message complet:\n{error[:300]}...')
