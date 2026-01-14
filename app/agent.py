# app/agent.py

import os
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
from app.tools import search_imt, send_email
from typing import Optional

load_dotenv()

# -------------------------
# Agent minimal et commenté
# -------------------------
# Principe :
# 1) Tenter d'utiliser le SDK officiel `google.generativeai` (Gemini) si installé.
# 2) Si le SDK n'est pas présent ou si l'appel échoue, utiliser une heuristique simple
#    pour décider entre deux actions : `SEARCH` (répondre) ou `EMAIL` (envoyer un e-mail).
# 3) Les outils `search_imt` et `send_email` restent inchangés et sont appelés selon la décision.

# Tentative d'import du SDK (optionnelle)
try:
    import google.generativeai as genai  # type: ignore
    GENAI_AVAILABLE = True
    API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if API_KEY:
        # Certaines versions du SDK demandent une configuration explicite
        try:
            genai.configure(api_key=API_KEY)
        except Exception:
            pass
except Exception:
    GENAI_AVAILABLE = False

def _call_gemini(prompt: str) -> Optional[str]:
    """Appelle Gemini via le SDK si disponible.

    Retourne la chaîne textuelle de la réponse, ou `None` en cas d'erreur.
    On garde la logique simple : on tente d'extraire le texte attendu, et on ignore
    les détails de shape propres à chaque version du SDK.
    """
    if not GENAI_AVAILABLE:
        return None

    try:
        resp = genai.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_output_tokens=128,
        )

        # Extraction prudente du texte selon shape possible
        if hasattr(resp, "candidates") and resp.candidates:
            return resp.candidates[0].content.strip()
        if hasattr(resp, "choices") and resp.choices:
            choice = resp.choices[0]
            if hasattr(choice, "message") and hasattr(choice.message, "content"):
                return choice.message.content.strip()
            if hasattr(choice, "text"):
                return choice.text.strip()

        return str(resp)
    except Exception:
        return None


def agent(question: str) -> str:
    """Fonction principale de l'agent.

    - Construit un prompt simple demandant `SEARCH` ou `EMAIL`.
    - Tente d'obtenir la décision via Gemini (_call_gemini).
    - Si échec, applique une heuristique de mots-clés.
    - Exécute ensuite l'outil approprié et retourne son résultat.
    """
    prompt = (
        "Tu es un agent pour l'IMT. Réponds UNIQUEMENT par SEARCH ou EMAIL.\n"
        f"Question : {question}\n"
    )

    decision = _call_gemini(prompt)

    # Si Gemini absent ou problème, heuristique simple basée sur mots-clés
    if not decision:
        q = question.lower()
        if any(k in q for k in ("directeur", "email", "envoyer", "envoye", "contact")):
            decision = "EMAIL"
        else:
            decision = "SEARCH"

    decision = decision.strip().upper()

    if "EMAIL" in decision:
        # Appel de l'outil d'envoi d'email (doit être défini dans `app.tools`)
        return send_email(subject="Demande d'informations", content=question)
    # Par défaut, on appelle la recherche
    return search_imt(question)


if __name__ == "__main__":
    print("🤖 Agent IMT prêt\n")
    print(agent("Quels sont les frais de scolarité à l'IMT ?"))
    print("\n---\n")
    print(agent("Envoie un email au directeur pour demander des informations."))