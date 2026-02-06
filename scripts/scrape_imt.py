#scripts/scrape_imt.py
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re

BASE_URL = "https://www.imt.sn"
PAGES = {
    "accueil": BASE_URL,
    "formations": f"{BASE_URL}/bachelor-sciences-et-ingenierie-du-numerique-iot-cyber-cloud/",
    "formations_generale": f"{BASE_URL}/2-bachelors-en-sciences-et-ingenierie/",
    "institut_mines_telecom": f"{BASE_URL}/institut-mines-telecom/",
    "qui_sommes_nous": f"{BASE_URL}/qui-sommes-nous/institut-mines-telecom-dakar/",
    "Edulab": f"{BASE_URL}/espace-edulab/",
    "contact": f"{BASE_URL}/contact/",
}

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def scrape_page(name, url):
    """Scraping optimisé - extrait contenu informatif + données structurées (adresse, email, tel)."""
    print(f"🚀 Scraping {name}...")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Nettoyage : supprimer les éléments parasites
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()

        # 2. Extraction de données structurées (emails, téléphones, adresses)
        structured_data = []
        
        # Extraire emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', str(soup))
        if emails:
            structured_data.append(f"📧 Contact : {', '.join(set(emails))}")
        
        # Extraire téléphones (format international et local)
        phones = re.findall(r'(?:\+221|00221)?\s*\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}', str(soup))
        if phones:
            structured_data.append(f"📞 Téléphone : {', '.join(set(phones))}")
        
        # Extraire adresses (recherche de patterns communs au Sénégal)
        address_patterns = [
            r'(?i)(rue|avenue|boulevard|route|quartier|zone|immeuble)[^<>]{5,100}(?:dakar|sénégal|senegal)',
            r'(?i)(?:dakar|sénégal|senegal)[^<>]{5,100}(?:rue|avenue|boulevard|quartier)',
        ]
        for pattern in address_patterns:
            addresses = re.findall(pattern, str(soup))
            if addresses:
                structured_data.append(f"📍 Adresse : {addresses[0]}")
                break
        
        # 3. Extraction de contenu textuel
        text_blocks = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'address', 'span']):
            text = tag.get_text().strip()
            # Garder le texte significatif (> 10 chars pour capturer plus d'infos)
            if len(text) > 10:
                text_blocks.append(text)

        # 4. Filtrage du bruit critique (blacklist améliorée)
        BLACKLIST = [
            "accepter les cookies", "refuser les cookies", "politique de confidentialité",
            "google analytics", "google recaptcha", "combien font", "captcha",
            "pistage dans votre navigateur", "réglages des polices google", 
            "intégrations de vidéo", "page mentions légales", "cookies et paramètres",
            "nous utilisons des cookies", "bloquer les cookies", "effacer les cookies",
            "services externes", "google webfonts", "google maps", "hébergeurs de vidéo",
            "adresse ip", "fai sont susceptibles", "rechargement de la page"
        ]
        
        def is_noise(line: str) -> bool:
            l = line.lower()
            return any(word in l for word in BLACKLIST) or len(line) < 15
        
        cleaned_blocks = [block for block in text_blocks if not is_noise(block)]
        
        # 5. Dédoublonnage (garder uniquement les blocs uniques)
        unique_blocks = []
        seen = set()
        for block in cleaned_blocks:
            normalized = re.sub(r'\s+', ' ', block.lower())  # Normaliser les espaces
            if normalized not in seen:
                seen.add(normalized)
                unique_blocks.append(block)

        # 6. Combiner données structurées + contenu
        final_content = structured_data + unique_blocks

        # 7. Sauvegarde
        if final_content:
            file_path = DATA_DIR / f"{name}.txt"
            file_path.write_text("\n\n".join(final_content), encoding="utf-8")
            print(f"✅ {name}.txt sauvegardé ({len(final_content)} blocs, dont {len(structured_data)} données structurées)")
        else:
            print(f"⚠️ Aucun contenu trouvé pour {name}")

    except Exception as e:
        print(f"❌ Erreur sur {name}: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 SCRAPING IMT DAKAR - Version Optimisée")
    print("=" * 60)
    
    for name, url in PAGES.items():
        scrape_page(name, url)
    
    print("\n" + "=" * 60)
    print("✅ Scraping terminé ! Relancez build_index.py pour reconstruire l'index.")
    print("=" * 60)