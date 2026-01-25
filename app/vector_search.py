# app/vector_search.py
"""
Moteur de recherche vectorielle utilisant Sentence-Transformers.
Remplace le scoring manuel basique par une recherche sémantique.
"""
from pathlib import Path
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict

DATA_DIR = Path("data")
EMBEDDINGS_FILE = DATA_DIR / "embeddings.pkl"

class VectorSearch:
    """Recherche sémantique vectorielle dans les documents IMT."""
    
    def __init__(self):
        """Charge l'index vectoriel et le modèle."""
        self.model = None
        self.chunks = []
        self.embeddings = None
        self._load_index()
    
    def _load_index(self):
        """Charge l'index vectoriel depuis le fichier."""
        if not EMBEDDINGS_FILE.exists():
            raise FileNotFoundError(
                f"❌ Index vectoriel introuvable : {EMBEDDINGS_FILE}\n"
                "Exécutez d'abord : python scripts/build_vector_index.py"
            )
        
        with open(EMBEDDINGS_FILE, 'rb') as f:
            data = pickle.load(f)
        
        self.chunks = data['chunks']
        self.embeddings = data['embeddings']
        model_name = data['model_name']
        
        # Charger le modèle (même que pour l'indexation)
        self.model = SentenceTransformer(model_name)
        
        print(f"✅ Index vectoriel chargé : {len(self.chunks)} chunks")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Recherche sémantique dans l'index.
        
        Args:
            query: Question de l'utilisateur
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste de chunks pertinents avec scores de similarité
        """
        # Générer embedding de la requête
        query_embedding = self.model.encode([query])[0]
        
        # Calculer similarité cosinus avec tous les chunks
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Trouver les top_k plus similaires
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'content': self.chunks[idx]['content'],
                'source': self.chunks[idx]['source'],
                'score': float(similarities[idx])
            })
        
        return results
    
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
