# scripts/build_index.py
from pathlib import Path
import json

DATA_DIR = Path("data")
INDEX_FILE = DATA_DIR / "chunks.json"

def build_index():
    chunks = []

    for txt_file in DATA_DIR.glob("*.txt"):
        text = txt_file.read_text(encoding="utf-8")

        chunk_size = 500
        overlap = 50
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunks.append({
                "source": txt_file.name,
                "content": text[start:end]
            })
            start += chunk_size - overlap

    INDEX_FILE.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Index créé avec succès ({len(chunks)} chunks)")

if __name__ == "__main__":
    build_index()