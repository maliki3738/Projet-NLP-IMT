from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

def build_index():
    path_txt = "data/imt_content.txt"
    persist_dir = "data/chroma_db"

    # 1. Vérification du fichier source
    if not os.path.exists(path_txt):
        print(f" Erreur : Le fichier {path_txt} est introuvable !")
        return

    print("Chargement du texte...")
    loader = TextLoader(path_txt, encoding="utf-8")
    documents = loader.load()
    
    # Vérification si le document est vide
    if not documents or len(documents[0].page_content) < 10:
        print(" Erreur : Le fichier imt_content.txt semble vide ou trop court.")
        return

    print(f" Texte chargé ({len(documents[0].page_content)} caractères)")

    # 2. Découpage en chunks (C'est ici qu'on règle le problème du "vide")
    print(" Découpage en morceaux (chunks)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f" Nombre de chunks créés : {len(chunks)}")

    # 3. Création de l'index vectoriel
    print("Création de l'index vectoriel (Embeddings)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # On crée la base de données
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    print(f" Index sauvegardé avec succès dans : {persist_dir}")

if __name__ == "__main__":
    build_index()