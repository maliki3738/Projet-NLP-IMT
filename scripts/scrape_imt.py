import requests
from bs4 import BeautifulSoup
import os

def scrape_imt():
    urls = ["https://www.imt.sn/", "https://www.imt.sn/bachelor-sciences-et-ingenierie-du-numerique-iot-cyber-cloud/","https://www.imt.sn/espace-edulab/","https://www.imt.sn/qui-sommes-nous/institut-mines-telecom-dakar/","https://www.imt.sn/contact/"]
    all_text = ""

    for url in urls:
        print(f"Scraping : {url}")
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Nettoyage : on ne prend que le texte informatif
        for tag in soup.find_all(['h1', 'h2', 'p', 'li']):
            text = tag.get_text().strip()
            if len(text) > 20: 
                all_text += text + "\n"

    # Sauvegarde dans data/
    os.makedirs('data', exist_ok=True)
    with open("data/imt_content.txt", "w", encoding="utf-8") as f:
        f.write(all_text)
    print("✅ Texte extrait et nettoyé dans data/imt_content.txt")

if __name__ == "__main__":
    scrape_imt()