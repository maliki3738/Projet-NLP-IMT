#!/usr/bin/env python3
"""Test RAG FAISS sans segfault (pas de multiprocessing)"""
import os
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from app.vector_search import vector_search_imt

questions = [
    "Quelles formations ?",
    "Comment contacter ?",
    "Bachelor cybersécurité ?"
]

print("=" * 80)
print("🧪 TEST RAG FAISS")
print("=" * 80)

for q in questions:
    print(f"\n❓ {q}")
    results = vector_search_imt(q, 3)
    for i, r in enumerate(results, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        print(f"{emoji} {r['score']:.3f} - {r['source'][:30]}")

print("\n✅ FAISS intégré avec succès!")