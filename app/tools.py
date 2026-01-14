# app/tools.py

def search_imt(query: str) -> str:
    """
    Simule une recherche d'information sur le site de l'IMT.
    (Sera remplacé plus tard par le vrai RAG)
    """
    return (
        "Informations IMT (simulation) :\n"
        "- Les frais de scolarité varient selon la formation.\n"
        "- L'IMT est situé à Dakar.\n"
        "- Plusieurs formations en numérique sont proposées."
    )


def send_email(subject: str, content: str) -> str:
    """
    Simule l'envoi d'un email au Directeur de l'IMT.
    """
    return (
        "EMAIL ENVOYÉ (simulation)\n"
        f"Sujet : {subject}\n"
        f"Contenu : {content}"
    )