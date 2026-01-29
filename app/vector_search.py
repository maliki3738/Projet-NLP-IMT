# app/vector_search.py
"""
Moteur de recherche vectorielle utilisant FAISS + Sentence-Transformers.
Remplace le scoring manuel basique par une recherche sémantique optimisée.
"""
from pathlib import Path
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
EMBEDDINGS_FILE = DATA_DIR / "embeddings.pkl"
FAISS_INDEX_FILE = DATA_DIR / "faiss.index"

# ✅ CHARGER SENTENCETRANSFORMER UNE SEULE FOIS (FIX SEGFAULT macOS)
# Ne jamais recréer le modèle pendant l'exécution
_EMBEDDING_MODEL = None

def get_embedding_model():
    """Retourne le modèle d'embeddings (singleton)."""
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        logger.info("🔄 Chargement du modèle d'embeddings (une seule fois)...")
        _EMBEDDING_MODEL = SentenceTransformer(
            "paraphrase-multilingual-MiniLM-L12-v2",
            device="cpu"
        )
        _EMBEDDING_MODEL.encode("test", show_progress_bar=False)  # Warmup
        logger.info("✅ Modèle d'embeddings chargé")
    return _EMBEDDING_MODEL

class VectorSearch:
    """Recherche sémantique vectorielle FAISS dans les documents IMT."""
    
    def __init__(self):
        """Charge l'index FAISS et le modèle."""
        self.model = None
        self.chunks = []
        self.index = None
        self._load_index()
    
    def _load_index(self):
        """Charge l'index FAISS et les métadonnées."""
        # Vérifier les fichiers
        if not FAISS_INDEX_FILE.exists():
            raise FileNotFoundError(
                f"❌ Index FAISS introuvable : {FAISS_INDEX_FILE}\n"
                "Exécutez d'abord : python scripts/build_vector_index.py"
            )
        
        if not EMBEDDINGS_FILE.exists():
            raise FileNotFoundError(
                f"❌ Métadonnées introuvables : {EMBEDDINGS_FILE}\n"
                "Exécutez d'abord : python scripts/build_vector_index.py"
            )
        
        # Charger l'index FAISS (avec protection)
        try:
            self.index = faiss.read_index(str(FAISS_INDEX_FILE))
        except Exception as e:
            logger.error(f"❌ Erreur chargement FAISS: {e}")
            raise
        
        # Charger les métadonnées
        with open(EMBEDDINGS_FILE, 'rb') as f:
            metadata = pickle.load(f)
        
        self.chunks = metadata['chunks']
        
        # ✅ Utiliser le modèle global (pas de recréation)
        self.model = get_embedding_model()
        
        print(f"✅ Index FAISS chargé : {len(self.chunks)} chunks (IndexFlatIP)")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Recherche sémantique FAISS dans l'index.
        
        Args:
            query: Question de l'utilisateur
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste de chunks pertinents avec scores de similarité
        """
        try:
            # Générer embedding de la requête
            query_embedding = self.model.encode([query], show_progress_bar=False, convert_to_numpy=True)
            
            # Normaliser pour similarité cosinus (comme lors de l'indexation)
            faiss.normalize_L2(query_embedding)
            
            # Recherche FAISS (retourne distances et indices)
            distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Construire les résultats
            results = []
            for idx, score in zip(indices[0], distances[0]):
                if idx < len(self.chunks):  # Vérification sécurité
                    results.append({
                        'content': self.chunks[idx]['content'],
                        'source': self.chunks[idx]['source'],
                        'score': float(score)  # Score = similarité cosinus (0-1)
                    })
            
            return results
        except Exception as e:
            logger.error(f"❌ Erreur FAISS search: {e}")
            return []  # Retourner liste vide plutôt que crasher
    
    def get_best_paragraph(self, query: str) -> tuple:
        """
        Retourne le meilleur paragraphe et sa source (compatibilité avec ancien code).
        
        Returns:
            (content, source, score)
        """
        results = self.search(query, top_k=1)
        if results:
            best = results[0]
            return best['content'], best['source'], best['score']
        return None, None, 0.0


# Instance globale (singleton)
_vector_search = None

def get_vector_search() -> VectorSearch:
    """Retourne l'instance du moteur de recherche (singleton)."""
    global _vector_search
    if _vector_search is None:
        _vector_search = VectorSearch()
    return _vector_search


# Fonction utilitaire pour compatibilité avec tools.py
def vector_search_imt(query: str, top_k: int = 3) -> List[Dict]:
    """
    Recherche vectorielle dans les documents IMT.
    
    Args:
        query: Question de l'utilisateur
        top_k: Nombre de résultats
        
    Returns:
        Liste de résultats avec content, source, score
    """
    searcher = get_vector_search()
    return searcher.search(query, top_k)
