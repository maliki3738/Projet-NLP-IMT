from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

def build_index():
    print(" Début de l'indexation...")
    
    # 1. Chargement du texte
    loader = TextLoader("data/imt_content.txt", encoding="utf-8")
    raw_docs = loader.load()
    
    # 2. Nettoyage rapide (enlever les lignes de cookies)
    cleaned_content = raw_docs[0].page_content
    # (Tu peux ajouter ici la logique de nettoyage citée plus haut)

    # 3. Découpage en chunks (Important pour le RAG)
    # On prend des morceaux de 600 caractères avec un petit recouvrement
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks = text_splitter.split_text(cleaned_content)

    # 4. Création des Embeddings et de l'index
    print("Création des vecteurs (Embeddings)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Sauvegarde locale dans data/chroma_db comme demandé
    vector_db = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory="data/chroma_db"
    )
    
    print("Index vectoriel créé avec succès dans data/chroma_db !")

if __name__ == "__main__":
    build_index()