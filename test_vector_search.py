#!/usr/bin/env python3
"""
Script de test du RAG vectoriel.
Compare l'ancien système de scoring vs la recherche sémantique.
"""
from app.vector_search import vector_search_imt

# Questions de test
test_questions = [
    "Quelles sont les formations proposées ?",
    "Comment s'inscrire à l'IMT ?",
    "Quel est le coût des études ?",
    "Quels sont les débouchés professionnels ?",
    "Où se trouve l'école ?",
    "Parlez-moi du bachelor IoT et cybersécurité",
    "Quels sont les partenaires de l'IMT ?",
    "Comment contacter l'école ?"
]

def test_vector_search():
    """Teste la recherche vectorielle sur plusieurs questions."""
    print("=" * 80)
    print("🧪 TEST DU RAG VECTORIEL - Recherche Sémantique")
    print("=" * 80)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*80}")
        print(f"📌 Question {i}/{len(test_questions)}: {question}")
        print(f"{'='*80}\n")
        
        results = vector_search_imt(question, top_k=3)
        
        for rank, result in enumerate(results, 1):
            score = result['score']
            source = result['source']
            content = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            
            print(f"🏆 Résultat #{rank}")
            print(f"   Score: {score:.3f}")
            print(f"   Source: {source}")
            print(f"   Contenu: {content}")
            print()

if __name__ == "__main__":
    test_vector_search()
