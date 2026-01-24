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
    print(f"Scraping {name}...")
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # On enlève scripts & styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    cleaned_text = "\n".join(
        line.strip() for line in text.splitlines() if line.strip()
    )

    # Nettoyage supplémentaire
    BLACKLIST = [
        "cookies",
        "confidentialité",
        "accepter",
        "refuser",
        "mentions légales",
        "ouvrir la barre",
        "uvrir",
        "ropos",
        "identialité",
        "cookie",
        "google analytics",
        "accepter les cookies",
        "champ",
        "validation",
        "test de vérification",
        "combien font",
        "pistage",
        "navigateur",
        "services externes",
        "google webfonts",
        "google maps",
        "hébergeurs de vidéo",
        "adresse ip",
        "fonctionnalités",
        "rechargement de la page",
        "polices google fonts",
        "google recaptcha",
        "intégrations de vidéo",
        "vimeo et youtube",
        "incorporation de vidéos"
    ]

    def is_noise(line: str) -> bool:
        l = line.lower()
        return any(word in l for word in BLACKLIST) or len(line) < 40

    cleaned_lines = [
        line for line in cleaned_text.splitlines()
        if not is_noise(line)
    ]

    file_path = DATA_DIR / f"{name}.txt"
    file_path.write_text("\n".join(cleaned_lines), encoding="utf-8")

if __name__ == "__main__":
    for name, url in PAGES.items():
        scrape_page(name, url)

    print("Scraping terminé")


# import requests
# from bs4 import BeautifulSoup
# import os

# def scrape_imt():
#     urls = ["https://www.imt.sn/", "https://www.imt.sn/bachelor-sciences-et-ingenierie-du-numerique-iot-cyber-cloud/","https://www.imt.sn/espace-edulab/","https://www.imt.sn/qui-sommes-nous/institut-mines-telecom-dakar/","https://www.imt.sn/contact/"]
#     all_text = ""

#     for url in urls:
#         print(f"Scraping : {url}")
#         res = requests.get(url)
#         soup = BeautifulSoup(res.text, 'html.parser')
        
#         # Nettoyage : on ne prend que le texte informatif
#         for tag in soup.find_all(['h1', 'h2', 'p', 'li']):
#             text = tag.get_text().strip()
#             if len(text) > 20: 
#                 all_text += text + "\n"

#     # Sauvegarde dans data/
#     os.makedirs('data', exist_ok=True)
#     with open("data/imt_content.txt", "w", encoding="utf-8") as f:
#         f.write(all_text)
#     print("✅ Texte extrait et nettoyé dans data/imt_content.txt")

# if __name__ == "__main__":
#     scrape_imt()