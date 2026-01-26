#!/usr/bin/env python3
"""
Test de l'agent LangChain simplifié.

Vérifie que l'agent fonctionne correctement avec Gemini.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.langchain_agent import create_imt_agent, run_agent
from dotenv import load_dotenv

load_dotenv()


def test_create_agent():
    """Test de création de l'agent."""
    print("🧪 Test 1: Création de l'agent...")
    try:
        agent = create_imt_agent()
        print(f"✅ Agent créé: {type(agent).__name__}")
        return agent
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


def test_simple_question(agent):
    """Test avec question simple."""
    print("\n🧪 Test 2: Question simple...")
    question = "Bonjour, qui es-tu ?"
    try:
        response = run_agent(question, agent)
        print(f"Question: {question}")
        print(f"Réponse ({len(response)} car.): {response[:200]}...")
        print("✅ Test réussi")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_search_question(agent):
    """Test avec question nécessitant recherche."""
    print("\n🧪 Test 3: Question avec recherche RAG...")
    question = "Quelles sont les formations proposées à l'IMT ?"
    try:
        response = run_agent(question, agent)
        print(f"Question: {question}")
        print(f"Réponse ({len(response)} car.): {response[:300]}...")
        
        # Vérifier que la réponse contient des informations pertinentes
        keywords = ['formation', 'master', 'bachelor', 'cybersécurité']
        found = [kw for kw in keywords if kw.lower() in response.lower()]
        print(f"Mots-clés trouvés: {found}")
        
        if found:
            print("✅ Test réussi (informations pertinentes)")
            return True
        else:
            print("⚠️  Réponse sans mots-clés attendus")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_auto_agent():
    """Test sans création d'agent (auto)."""
    print("\n🧪 Test 4: Mode auto (sans agent pré-créé)...")
    question = "Dis-moi l'adresse de contact de l'IMT"
    try:
        response = run_agent(question)  # Sans agent
        print(f"Question: {question}")
        print(f"Réponse ({len(response)} car.): {response[:200]}...")
        print("✅ Test réussi")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    """Exécuter tous les tests."""
    print("=" * 60)
    print("🧪 TEST AGENT LANGCHAIN SIMPLIFIÉ")
    print("=" * 60)
    
    # Vérifier clé API
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERREUR: GEMINI_API_KEY manquante dans .env")
        print("Ajoutez GEMINI_API_KEY=<votre_clé> dans le fichier .env")
        return False
    
    results = []
    
    # Test 1: Création
    agent = test_create_agent()
    results.append(agent is not None)
    
    if agent:
        # Test 2: Question simple
        results.append(test_simple_question(agent))
        
        # Test 3: Question avec recherche
        results.append(test_search_question(agent))
    else:
        print("\n⏭️  Tests 2-3 sautés (agent non créé)")
        results.extend([False, False])
    
    # Test 4: Mode auto
    results.append(test_auto_agent())
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    success = sum(results)
    total = len(results)
    print(f"Tests réussis: {success}/{total} ({success*100//total}%)")
    
    if success == total:
        print("✅ Tous les tests passent - Agent LangChain opérationnel!")
        return True
    else:
        print(f"⚠️  {total - success} test(s) échoué(s)")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
