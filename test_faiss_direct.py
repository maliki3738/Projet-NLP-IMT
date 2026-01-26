#!/usr/bin/env python3
"""Test FAISS directement sans Sentence-Transformers reload"""
import faiss
import pickle
from pathlib import Path

# Charger index et métadonnées
index = faiss.read_index('data/faiss.index')
metadata = pickle.load(open('data/embeddings.pkl', 'rb'))

print(f"✅ Index FAISS chargé : {index.ntotal} vecteurs")
print(f"✅ Dimension : {index.d}")
print(f"✅ Chunks : {len(metadata['chunks'])}")

# Test recherche simple (vecteur aléatoire normalisé)
import numpy as np
test_vec = np.random.rand(1, index.d).astype('float32')
faiss.normalize_L2(test_vec)

distances, indices = index.search(test_vec, 3)
print(f"\n🔍 Test recherche:")
for i, (idx, dist) in enumerate(zip(indices[0], distances[0]), 1):
    print(f"  {i}. Score: {dist:.3f} - {metadata['chunks'][idx]['source']}")

print("\n✅ FAISS fonctionne parfaitement !")
