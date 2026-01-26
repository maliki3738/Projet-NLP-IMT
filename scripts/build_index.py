# scripts/build_index.py
"""
Script pour créer l'index JSON des chunks à partir des fichiers .txt
Ce script est obsolète - utilisez build_vector_index.py à la place pour FAISS
"""
from pathlib import Path
import json
import re

DATA_DIR = Path("data")
INDEX_FILE = DATA_DIR / "chunks.json"

def clean_text(text):
    """Nettoie le texte en supprimant les espaces multiples et lignes vides."""
    text = re.sub(r'\n\s*\n+', '\n\n', text)  # Réduire lignes vides multiples
    text = re.sub(r' +', ' ', text)  # Réduire espaces multiples
    return text.strip()

def split_into_paragraphs(text):
    """Découpe le texte en paragraphes cohérents (minimum 30 caractères)."""
    # Séparer par double saut de ligne (paragraphes)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    # Filtrer les paragraphes trop courts (titres seuls, etc.)
    valid_paragraphs = []
    for para in paragraphs:
        if len(para) >= 30:  # Minimum 30 chars pour éviter titres isolés
            valid_paragraphs.append(para)
    
    return valid_paragraphs

def build_index():
    """Construit l'index de recherche avec découpage intelligent par paragraphes."""
    chunks = []

    for txt_file in DATA_DIR.glob("*.txt"):
        raw_text = txt_file.read_text(encoding="utf-8")
        cleaned_text = clean_text(raw_text)
        
        paragraphs = split_into_paragraphs(cleaned_text)
        
        for paragraph in paragraphs:
            chunks.append({
                "source": txt_file.name,
                "content": paragraph
            })

    # Sauvegarder dans chunks.json
    INDEX_FILE.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"✅ Index créé avec succès ({len(chunks)} chunks)")
    print(f"📄 Fichiers traités : {len(list(DATA_DIR.glob('*.txt')))}")
    print(f"💾 Sauvegardé dans : {INDEX_FILE}")

if __name__ == "__main__":
    build_index()