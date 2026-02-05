#!/usr/bin/env python3
"""
Test de l'agent intelligent en mode CLI pour voir le raisonnement.
"""
import sys
from app.langchain_agent import create_imt_agent, run_agent

def test_reasoning():
    """Teste le raisonnement de l'agent avec différentes questions."""
    
    print("=" * 70)
    print("🧠 TEST RAISONNEMENT AGENT INTELLIGENT")
    print("=" * 70)
    print()
    
    # Créer l'agent
    print("⚙️  Initialisation de l'agent Gemini...")
    try:
        agent = create_imt_agent(verbose=False)
        print("✅ Agent initialisé avec succès")
        print()
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return
    
    # Questions de test
    questions = [
        {
            "id": 1,
            "question": "Bonjour !",
            "type": "Salutation (pas d'outil)",
            "attendu": "Réponse directe sans recherche"
        },
        {
            "id": 2,
            "question": "Quelles sont les formations proposées à l'IMT ?",
            "type": "Question RAG (avec search_imt)",
            "attendu": "Recherche + synthèse des formations"
        },
        {
            "id": 3,
            "question": "Comment puis-je vous contacter ?",
            "type": "Question contact (info ou email)",
            "attendu": "Infos contact ou proposition d'email"
        },
    ]
    
    # Tester chaque question
    for i, test in enumerate(questions, 1):
        print(f"{'─' * 70}")
        print(f"📝 TEST {test['id']}/3 : {test['type']}")
        print(f"{'─' * 70}")
        print()
        print(f"❓ Question : \"{test['question']}\"")
        print(f"🎯 Attendu  : {test['attendu']}")
        print()
        print("🧠 Raisonnement de l'agent :")
        print("-" * 70)
        
        try:
            # Appeler l'agent (les logs montrent le raisonnement)
            response = run_agent(test['question'], agent)
            
            print("-" * 70)
            print()
            print(f"💬 Réponse de l'agent :")
            print()
            print(response)
            print()
            
            # Succès
            print(f"✅ Test {test['id']} réussi")
            print()
            
        except Exception as e:
            print(f"❌ Erreur : {e}")
            print()
    
    print("=" * 70)
    print("🎉 Tests terminés")
    print("=" * 70)


if __name__ == "__main__":
    print()
    test_reasoning()
    print()
