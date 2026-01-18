# app/tools.py
import json
from difflib import get_close_matches

def search_imt(query: str) -> str:
    q_lower = query.lower()
    
    # Exception pour les questions de localisation
    if any(word in q_lower for word in ["où", "ou", "adresse", "localisation", "lieu", "emplacement"]):
        try:
            with open("data/chunks.json", "r", encoding="utf-8") as f:
                chunks = json.load(f)
        except FileNotFoundError:
            return "Les données IMT ne sont pas encore indexées."
        for chunk in chunks:
            if chunk["source"] == "contact.txt":
                lines = chunk["content"].split('\n')
                for line in lines:
                    if "avenue" in line.lower() or "dakar" in line.lower():
                        return line.strip()
        return "Adresse non trouvée."
    
    try:
        with open("data/chunks.json", "r", encoding="utf-8") as f:
            chunks = json.load(f)
    except FileNotFoundError:
        return "Les données IMT ne sont pas encore indexées."

    query_words = set(q_lower.split())
    
    # Trouver le chunk avec le plus de matches dans le contenu entier
    best_chunk = None
    max_matches = 0
    for chunk in chunks:
        content_lower = chunk["content"].lower()
        match_count = sum(1 for word in query_words if word in content_lower)
        if match_count > max_matches:
            max_matches = match_count
            best_chunk = chunk
    
    if not best_chunk or max_matches == 0:
        return "Aucune information trouvée sur cette question."
    
    # Extraire la ligne la plus pertinente du chunk
    lines = best_chunk["content"].split('\n')
    relevant_lines = [line.strip() for line in lines if len(line) > 10 and any(word in line.lower() for word in query_words)]
    
    if relevant_lines:
        # Retourner seulement la première ligne pertinente, nettoyée
        line = relevant_lines[0]
        # Nettoyer les préfixes comme [EVENEMENT]
        if line.startswith('[') and ']' in line:
            line = line.split(']', 1)[1].strip()
        return line
    else:
        return "Aucune information pertinente trouvée."

def send_email(subject: str, content: str) -> str:
    """
    Simule l'envoi d'un email au Directeur de l'IMT.
    """
    return (
        "EMAIL ENVOYÉ (simulation)\n"
        f"Sujet : {subject}\n"
        f"Contenu : {content}"
    )