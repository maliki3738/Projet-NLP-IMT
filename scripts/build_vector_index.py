# scripts/build_vector_index.py
"""
Construit un index vectoriel FAISS à partir des chunks de texte.
Utilise Sentence-Transformers pour générer des embeddings sémantiques.
"""
from pathlib import Path
import json
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

DATA_DIR = Path("data")
CHUNKS_FILE = DATA_DIR / "chunks.json"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.pkl"
FAISS_INDEX_FILE = DATA_DIR / "faiss.index"

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
    
    # 3. Générer les embeddings (par petits batchs pour éviter segfault)
    print("🔄 Génération des embeddings...")
    texts = [chunk['content'] for chunk in chunks]
    
    # Encoder en une seule fois SANS show_progress_bar (cause du segfault)
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    embeddings = embeddings.astype('float32')
    print(f"✅ Embeddings générés : {embeddings.shape}")
    
    # 4. Créer l'index FAISS (IndexFlatIP pour similarité cosinus)
    print("🔧 Création de l'index FAISS...")
    dimension = embeddings.shape[1]
    
    # Normaliser les embeddings pour utiliser IndexFlatIP (similarité cosinus)
    faiss.normalize_L2(embeddings)
    
    # Créer l'index FAISS (Flat = recherche exhaustive, IP = Inner Product)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype('float32'))
    
    # 5. Sauvegarder l'index FAISS
    print("💾 Sauvegarde de l'index FAISS...")
    faiss.write_index(index, str(FAISS_INDEX_FILE))
    
    # 6. Sauvegarder les métadonnées (chunks) séparément
    metadata = {
        'chunks': chunks,
        'model_name': 'paraphrase-multilingual-MiniLM-L12-v2'
    }
    
    with open(EMBEDDINGS_FILE, 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"✅ Index FAISS créé avec succès !")
    print(f"   - {len(chunks)} chunks indexés")
    print(f"   - Dimension embeddings : {dimension}")
    print(f"   - Index FAISS : {FAISS_INDEX_FILE}")
    print(f"   - Métadonnées : {EMBEDDINGS_FILE}")
    print(f"   - Type index : IndexFlatIP (similarité cosinus)")

if __name__ == "__main__":
    build_vector_index()
