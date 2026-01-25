# scripts/build_vector_index.py
"""
Construit un index vectoriel FAISS à partir des chunks de texte.
Utilise Sentence-Transformers pour générer des embeddings sémantiques.
"""
from pathlib import Path
import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

DATA_DIR = Path("data")
CHUNKS_FILE = DATA_DIR / "chunks.json"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.pkl"
INDEX_FILE = DATA_DIR / "faiss_index.pkl"

def build_vector_index():
    """Crée l'index vectoriel FAISS à partir des chunks."""
    
    # 1. Charger les chunks
    print("📂 Chargement des chunks...")
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"✅ {len(chunks)} chunks chargés")
    
    # 2. Charger le modèle d'embeddings (multilingue français)
    print("🤖 Chargement du modèle Sentence-Transformer...")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    # 3. Générer les embeddings
    print("🔄 Génération des embeddings...")
    texts = [chunk['content'] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # 4. Sauvegarder les embeddings et métadonnées
    print("💾 Sauvegarde de l'index...")
    data = {
        'chunks': chunks,
        'embeddings': embeddings,
        'model_name': 'paraphrase-multilingual-MiniLM-L12-v2'
    }
    
    with open(EMBEDDINGS_FILE, 'wb') as f:
        pickle.dump(data, f)
    
    print(f"✅ Index vectoriel créé avec succès !")
    print(f"   - {len(chunks)} chunks")
    print(f"   - Dimension embeddings : {embeddings.shape[1]}")
    print(f"   - Fichier : {EMBEDDINGS_FILE}")

if __name__ == "__main__":
    build_vector_index()
