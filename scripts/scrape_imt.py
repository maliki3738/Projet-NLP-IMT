#scripts/scrape_imt.py
import requests
from bs4 import BeautifulSoup
from pathlib import Path

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
DATA_DIR.mkdir(exist_ok=True
)

def scrape_page(name, url):
    """Scraping simple et efficace - extrait uniquement le contenu informatif."""
    print(f"🚀 Scraping {name}...")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Nettoyage : supprimer les éléments parasites
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
            tag.decompose()

        # 2. Extraction simple et efficace : TOUT le document (pas de ciblage restrictif)
        # Car le ciblage de content_area était trop restrictif et ne trouvait qu'un titre
        text_blocks = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
            text = tag.get_text().strip()
            # Garder le texte significatif (> 15 chars pour éviter les fragments)
            if len(text) > 15:
                text_blocks.append(text)

        # 3. Filtrage du bruit critique
        BLACKLIST = [
            "accepter les cookies", "refuser les cookies", "politique de confidentialité",
            "google analytics", "google recaptcha", "combien font",
            "pistage dans votre navigateur", "réglages des polices google", 
            "intégrations de vidéo", "page mentions légales"
        ]
        
        def is_noise(line: str) -> bool:
            l = line.lower()
            return any(word in l for word in BLACKLIST)
        
        cleaned_blocks = [block for block in text_blocks if not is_noise(block)]

        # 4. Sauvegarde
        if cleaned_blocks:
            file_path = DATA_DIR / f"{name}.txt"
            file_path.write_text("\n\n".join(cleaned_blocks), encoding="utf-8")
            print(f"✅ {name}.txt sauvegardé ({len(cleaned_blocks)} blocs de texte)")
        else:
            print(f"⚠️ Aucun contenu trouvé pour {name}")

    except Exception as e:
        print(f"❌ Erreur sur {name}: {e}")


if __name__ == "__main__":
    for name, url in PAGES.items():
        scrape_page(name, url)

    print("Scraping terminé")