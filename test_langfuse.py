from dotenv import load_dotenv
import os
from langfuse import Langfuse

# 1. Charger le .env
load_dotenv()

# 2. Vérifier les clés
public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

print("🔍 Vérification des variables d'environnement:")
print(f"   LANGFUSE_PUBLIC_KEY: {'✅ Présente' if public_key else '❌ ABSENTE'}")
print(f"   LANGFUSE_SECRET_KEY: {'✅ Présente' if secret_key else '❌ ABSENTE'}")
print(f"   LANGFUSE_HOST: {host}")

if not public_key or not secret_key:
    print("\n❌ ÉCHEC : Les clés Langfuse ne sont pas configurées dans .env")
    print("\n📋 Instructions:")
    print("   1. Créer un compte sur https://cloud.langfuse.com")
    print("   2. Récupérer les clés API (Settings → API Keys)")
    print("   3. Ajouter dans .env :")
    print("      LANGFUSE_PUBLIC_KEY=pk-lf-...")
    print("      LANGFUSE_SECRET_KEY=sk-lf-...")
    print("      LANGFUSE_HOST=https://cloud.langfuse.com")
    print("\n📖 Voir docs/GUIDE_LANGFUSE.md pour le guide complet")
    exit(1)

# 3. Initialiser Langfuse
try:
    langfuse = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=host,
    )
    print("\n✅ Langfuse client initialisé avec succès")
except Exception as e:
    print(f"\n❌ ERREUR lors de l'initialisation : {e}")
    exit(1)

# 4. Créer une trace de test
try:
    print("\n🧪 Envoi d'une trace de test...")
    
    # API Langfuse 3.x : utiliser create_event (plus simple pour un test)
    event = langfuse.create_event(
        name="test-langfuse",
        metadata={"test": True, "source": "test_script"},
        input={"message": "hello langfuse"},
        output={"response": "langfuse fonctionne !"}
    )
    
    print("✅ Événement envoyé avec succès")
    print(f"   Event ID: {event.id}")
    print(f"   🌐 Dashboard: {host}")
    
    # Forcer l'envoi immédiat
    langfuse.flush()
    
    print("\n🎉 Test Langfuse réussi !")
    print("   ➜ Allez sur https://cloud.langfuse.com")
    print("   ➜ Sélectionnez votre projet")
    print("   ➜ Onglet 'Traces' pour voir l'événement 'test-langfuse'")
    print("\n💡 Le code dans app/agent.py utilise une API plus complexe")
    print("   avec start_generation() pour tracer les appels LLM complets")
    
except Exception as e:
    print(f"\n❌ ERREUR lors de la création de la trace : {e}")
    import traceback
    traceback.print_exc()
    exit(1)