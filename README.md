# IMT AI Agent

Agent conversationnel prototype pour l'IMT — objectifs :
- Répondre aux questions sur l'IMT (formations, frais, localisation)
- Effectuer des actions simples (ex. envoyer un e-mail de contact)

## Stack (prototype)
- LLM : Gemini (via le SDK `google-generativeai`)
- Orchestration : prototype maison (agent simple) — possibilité d'intégrer LangChain plus tard
- Interface : Chainlit (optionnelle)
- Mémoire : Redis (optionnelle)
- Observabilité : Langfuse (optionnelle)

## Variables d'environnement
Créez un fichier `.env` à la racine du projet pour stocker vos clés :

GEMINI_API_KEY=sk-...

Le projet utilise `python-dotenv` pour charger automatiquement `.env` si installé.

## Installation minimale (local)
```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` contient les dépendances minimales pour le prototype (`python-dotenv`, `google-generativeai`).

## Lancer l'agent
Depuis la racine du projet :

```bash
python -m app.agent
```

## Remarques
- Le code actuel utilise un agent simple (décision `SEARCH` vs `EMAIL`) et appelle `app.tools` pour les actions.\
- Pour passer à un système RAG / mémoire / UI, intégrer ces composants progressivement (retriever vectoriel, Redis, Chainlit).\
- Si vous souhaitez, je peux ajouter une section ``Développement`` avec instructions pour tester et déboguer localement.

Le module RAG utilise une indexation locale simplifiée (chunks + similarité textuelle), afin d’éviter les conflits de dépendances et garantir la stabilité du projet.