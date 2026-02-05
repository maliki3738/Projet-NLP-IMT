#!/usr/bin/env python3
"""
Test du RAG vectoriel seul (SANS appel LLM).
Permet de tester même quand tous les quotas API sont épuisés.
"""
from app.vector_search import vector_search_imt

# Questions de test
questions = [
    "Quelles formations proposez-vous ?",
    "Comment vous contacter ?",
    "Où se trouve l'école ?",
    "Parlez-moi du bachelor en cybersécurité",
    "C'est quoi l'IMT ?"
]

print("=" * 80)
print("🧪 TEST RAG VECTORIEL SEUL (Sans LLM)")
print("=" * 80)
print("\n✅ Idéal quand quotas API épuisés (Grok 429, OpenAI 429, Gemini 429)\n")

for i, question in enumerate(questions, 1):
    print(f"\n{'='*80}")
    print(f"📌 Question {i}: {question}")
    print(f"{'='*80}\n")
    
    results = vector_search_imt(question, top_k=3)
    
    for rank, result in enumerate(results, 1):
        score = result['score']
        source = result['source']
        content = result['content'][:150] + "..." if len(result['content']) > 150 else result['content']
        
        # Emojis selon score
        emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        
        print(f"{emoji} Résultat #{rank}")
        print(f"   📊 Score: {score:.3f}")
        print(f"   📄 Source: {source}")
        print(f"   💬 Contenu: {content}")
        print()

print("\n" + "=" * 80)
print("✅ Test terminé ! Le RAG fonctionne indépendamment des LLM.")
print("=" * 80)
