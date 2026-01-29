# app/simple_search.py
"""
Recherche texte SIMPLE sans FAISS (évite segfault).
Utilise regex et scoring basique pour trouver les meilleurs paragraphes.
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

DATA_DIR = Path("data")

# Mots-clés pour router les questions vers les bons fichiers
ROUTING_KEYWORDS = {
    "formations.txt": [
        "formation", "programme", "cursus", "diplôme", "bac", "master", 
        "ingénieur", "licence", "étude", "filière", "spécialité"
    ],
    "qui_sommes_nous.txt": [
        "histoire", "création", "fondation", "mission", "vision", 
        "objectif", "qui sommes", "qui êtes", "présentation"
    ],
    "contact.txt": [
        "contact", "téléphone", "email", "adresse", "localisation",
        "situer", "trouver", "appeler", "joindre", "écrire", "où", "lieu", "km"
    ],
    "institut_mines_telecom.txt": [
        "imt", "mines télécom", "télécom", "qu'est-ce", "c'est quoi",
        "définition", "réseau", "groupe"
    ],
    "accueil.txt": [
        "accueil", "bienvenue", "général", "présentation générale"
    ],
    "Edulab.txt": [
        "edulab", "laboratoire", "recherche", "innovation", "projet",
        "adresse", "situé", "localisation", "où", "avenue", "lieu", "anta diop"
    ],
    "formations_generale.txt": [
        "admission", "inscription", "candidature", "prérequis",
        "condition", "dossier", "frais", "coût", "prix"
    ]
}


def load_documents() -> Dict[str, str]:
    """Charge tous les documents texte depuis data/."""
    documents = {}
    
    for file in DATA_DIR.glob("*.txt"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                documents[file.name] = f.read()
        except Exception as e:
            logger.warning(f"Impossible de lire {file.name}: {e}")
    
    logger.info(f"✅ {len(documents)} documents chargés")
    return documents


def route_query(query: str) -> List[str]:
    """
    Détermine quels fichiers sont pertinents pour la question.
    
    Returns:
        Liste des fichiers à chercher (ordre de priorité)
    """
    query_lower = query.lower()
    scores = {}
    
    for file, keywords in ROUTING_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[file] = score
    
    # Trier par score décroissant
    sorted_files = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Si aucun match, chercher dans tous les fichiers
    if not sorted_files:
        return list(ROUTING_KEYWORDS.keys())
    
    # Retourner top 3 fichiers
    result = [file for file, _ in sorted_files[:3]]
    logger.info(f"🎯 Routing: {query[:50]}... → {result}")
    return result


def extract_paragraphs(text: str) -> List[str]:
    """Découpe le texte en paragraphes pertinents."""
    # Séparer par double saut de ligne
    paragraphs = re.split(r'\n\s*\n', text)
    
    # Mots à ignorer (bruit, cookies, etc.)
    ignore_keywords = ['cookie', 'rgpd', 'données personnelles', 'consentement', 'tracking']
    
    # Nettoyer et filtrer
    cleaned = []
    for p in paragraphs:
        p = p.strip()
        p_lower = p.lower()
        
        # Skip si contient trop de mots à ignorer
        if any(kw in p_lower for kw in ignore_keywords):
            continue
        
        # Garder seulement si > 50 caractères
        if len(p) > 50:
            cleaned.append(p)
    
    return cleaned


def score_paragraph(paragraph: str, query: str) -> float:
    """
    Score un paragraphe par rapport à la question.
    
    Returns:
        Score entre 0 et 1
    """
    para_lower = paragraph.lower()
    query_lower = query.lower()
    
    # Synonymes et variantes pour améliorer le matching
    expansions = {
        'formation': ['bachelor', 'master', 'diplôme', 'programme', 'cursus', 'étude'],
        'contact': ['téléphone', 'email', 'adresse', 'joindre', 'appeler'],
        'localisation': ['situé', 'adresse', 'trouve', 'où', 'lieu', 'km', 'avenue'],
        'situé': ['localisation', 'adresse', 'trouve', 'où', 'lieu', 'km', 'avenue'],
        'adresse': ['localisation', 'situé', 'trouve', 'où', 'lieu', 'km', 'avenue'],
        'où': ['localisation', 'situé', 'adresse', 'trouve', 'lieu', 'km', 'avenue'],
        'prix': ['frais', 'coût', 'tarif', 'montant'],
        'imt': ['institut', 'mines', 'télécom'],
    }
    
    # Extraire les mots importants de la question (> 3 caractères)
    query_words = [w for w in re.findall(r'\w+', query_lower) if len(w) > 3]
    
    if not query_words:
        return 0.0
    
    score = 0.0
    
    # Compter les matches directs + expansions
    for word in query_words:
        # Match direct
        if word in para_lower:
            score += 0.3
        # Match via synonymes
        elif word in expansions:
            for synonym in expansions[word]:
                if synonym in para_lower:
                    score += 0.2
                    break
    
    # Bonus si contient plusieurs mots ensemble
    matched_words = len([w for w in query_words if w in para_lower])
    if matched_words >= 2:
        score += 0.3
    
    # Bonus si paragraphe pas trop long (plus ciblé)
    if len(paragraph) < 500:
        score += 0.1
    
    return min(score, 1.0)


def search_documents(query: str, documents: Dict[str, str], top_k: int = 3) -> List[Dict]:
    """
    Recherche dans les documents.
    
    Returns:
        Liste de {content, source, score}
    """
    # Router la question
    target_files = route_query(query)
    
    results = []
    
    for filename in target_files:
        if filename not in documents:
            continue
        
        text = documents[filename]
        paragraphs = extract_paragraphs(text)
        
        for para in paragraphs:
            score = score_paragraph(para, query)
            if score >= 0.1:  # Accepter score = 0.1 (bonus paragraphe court)
                results.append({
                    'content': para,
                    'source': filename,
                    'score': score
                })
    
    # Trier par score décroissant
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Retourner top_k
    return results[:top_k]


def simple_search_imt(query: str) -> str:
    """
    Fonction principale de recherche (compatible avec tools.py).
    
    Returns:
        Contexte formaté avec les meilleurs résultats
    """
    try:
        documents = load_documents()
        results = search_documents(query, documents, top_k=3)
        
        if not results:
            logger.warning(f"Aucun résultat pour: {query}")
            return ""
        
        # Formater le contexte
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Source: {result['source']}, Score: {result['score']:.2f}]\n"
                f"{result['content']}"
            )
        
        context = "\n\n===\n\n".join(context_parts)
        
        best = results[0]
        logger.info(f"✅ Meilleur résultat: {best['source']} (score: {best['score']:.2f})")
        
        return context
        
    except Exception as e:
        logger.error(f"❌ Erreur recherche: {e}")
        return ""


# Test rapide
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test 1
    print("=" * 60)
    print("TEST 1: Formations")
    print("=" * 60)
    result = simple_search_imt("Quelles sont les formations proposées ?")
    print(result[:300] + "...")
    
    # Test 2
    print("\n" + "=" * 60)
    print("TEST 2: Contact")
    print("=" * 60)
    result = simple_search_imt("Comment contacter l'IMT ?")
    print(result[:300] + "...")
