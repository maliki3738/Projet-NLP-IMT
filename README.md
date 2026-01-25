# 🤖 IMT AI Agent

Agent conversationnel intelligent pour l'Institut Mines-Télécom Dakar avec **RAG vectoriel**, **multi-LLM** et **observabilité complète**.

## 🎯 Fonctionnalités

✅ **RAG Vectoriel** : Recherche sémantique avec Sentence-Transformers (147 chunks indexés)  
✅ **Multi-LLM** : Cascade Grok → OpenAI → Gemini avec fallback intelligent  
✅ **Réponse aux questions** : Formations, contact, débouchés, histoire IMT  
✅ **Envoi d'emails** : SMTP avec validation robuste (Gmail, Outlook)  
✅ **Mémoire persistante** : Redis avec entités personnelles (nom, email, profil)  
✅ **Observabilité** : Langfuse pour traçabilité des appels LLM  
✅ **Interface moderne** : Chainlit avec agent LangChain ou classique  
✅ **Tests complets** : pytest + tests RAG vectoriel  

## 📚 Stack Technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| **LLM Primaire** | Grok (xAI) | grok-beta |
| **LLM Fallback 1** | OpenAI | gpt-4o-mini (0.15$/1M tokens) |
| **LLM Fallback 2** | Google Gemini | gemini-2.0-flash-exp |
| **RAG** | Sentence-Transformers | paraphrase-multilingual-MiniLM-L12-v2 |
| **Indexation** | Pickle | 147 chunks (embeddings 384D) |
| **Orchestration** | LangChain | 0.1.0 (agent ReAct) |
| **Interface** | Chainlit | 1.1.301 |
| **Mémoire** | Redis | 5.0.1 (fallback RAM) |
| **Observabilité** | Langfuse | cloud.langfuse.com |
| **Tests** | pytest | 9.0.2 |
| **Python** | 3.11 | (Chainlit incompatible 3.13) |

## 🏗️ Architecture

```
┌─────────────────┐
│  Utilisateur    │
└────────┬────────┘
         │
    ┌────▼─────────────────┐
    │  Chainlit Interface  │
    └────┬─────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │         Agent (app/agent.py)          │
    │  ┌─────────────────────────────────┐  │
    │  │ 1. Grok (prioritaire)           │  │
    │  │ 2. OpenAI GPT-4o-mini           │  │
    │  │ 3. Gemini 2.0 Flash             │  │
    │  │ 4. Fallback heuristique         │  │
    │  └─────────────────────────────────┘  │
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────┬──────────────────┐
    │                   │                  │
┌───▼────────┐  ┌───────▼───────┐  ┌──────▼───────┐
│ RAG Search │  │  Send Email   │  │    Redis     │
│ (vector)   │  │  (SMTP)       │  │   Memory     │
└────────────┘  └───────────────┘  └──────────────┘
```

## 🚀 Installation Rapide

### 1. Cloner et configurer l'environnement

```bash
# Cloner le projet
cd /path/to/imt-agent-clean

# Créer environnement virtuel Python 3.11
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou venv\Scripts\activate sur Windows

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Construire l'index RAG vectoriel
python scripts/build_index.py       # Crée chunks.json (147 paragraphes)
python scripts/build_vector_index.py # Crée embeddings.pkl (384D)
```

### 2. Configuration des variables d'environnement

Créer un fichier `.env` à la racine :

```env
# === LLM Configuration ===
# Grok (prioritaire)
XAI_API_KEY=xai-xxxxxxxxxxxxx  # https://x.ai

# OpenAI (fallback 1) - 5$ minimum, 0.04-0.32$/semaine usage réel
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx  # https://platform.openai.com

# Gemini (fallback 2)
GEMINI_API_KEY=AIzaSyBxxxxxxxxxxxxx  # https://ai.google.dev

# === Langfuse (observabilité) ===
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com

# === Agent Configuration ===
USE_LANGCHAIN_AGENT=true  # true = LangChain, false = agent classique

# === Email SMTP (optionnel) ===
EMAIL_USER=votre_email@gmail.com
EMAIL_PASS=mot_de_passe_application  # Voir docs/GUIDE_SMTP.md
EMAIL_TO=destinataire@example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# === Redis (optionnel - fallback RAM) ===
REDIS_HOST=localhost
REDIS_PORT=6379
```

📖 **Guides détaillés** :
- [docs/GUIDE_OPENAI.md](docs/GUIDE_OPENAI.md) : Configuration OpenAI + coûts
- [docs/GUIDE_LANGFUSE.md](docs/GUIDE_LANGFUSE.md) : Configuration observabilité
- [docs/GUIDE_SMTP.md](docs/GUIDE_SMTP.md) : Configuration email

### 3. Vérifier l'installation

```bash
# Tester RAG vectoriel
python test_vector_search.py

# Tester agent complet
python test_agent_rag.py

# Lancer interface Chainlit
chainlit run chainlit_app.py
```

## 💬 Utilisation

### Mode Console (Simple)

```bash
python -m app.agent
```

**Exemple** :
```
Vous : Quelles sont les formations disponibles à l'IMT ?
Agent : [Recherche dans la base et répond]

Vous : Envoie un email au directeur pour demander plus d'infos
Agent : [Envoie l'email et confirme]
```

### Mode Chainlit (Interface Web)

```bash
chainlit run chainlit_app.py
```

Ouvrir http://localhost:8000 dans votre navigateur.

**Interface graphique** avec :
- 💬 Chat en temps réel
- 📜 Historique des conversations
- 🎨 Interface moderne et responsive

## 🧪 Tests

### Exécuter tous les tests

```bash
pytest -v
```

### Tests par catégorie

```bash
# Tests de l'agent (22 tests)
pytest tests/test_agent.py -v

# Tests des outils (18 tests)
pytest tests/test_tools.py -v
```

### Couverture actuelle

| Module | Tests | Couverture |
|--------|-------|------------|
| `app/agent.py` | 20 | ~95% |
| `app/langchain_agent.py` | 18 | ~90% |
| `app/tools.py` | 18 | ~90% |
| **TOTAL** | **56** | **~91%** |

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [GUIDE_SMTP.md](docs/GUIDE_SMTP.md) | Configuration email Gmail/Outlook (350+ lignes) |
| [PLAN_DEVELOPPEMENT.md](docs/PLAN_DEVELOPPEMENT.md) | Roadmap 7 jours du projet |
| [RAPPORT_JOUR0.md](docs/RAPPORT_JOUR0.md) | Préparation et diagnostic initial |
## 🛠️ Architecture

```
imt-agent-clean/
├── app/
│   ├── agent.py            # Agent multi-LLM (Grok→OpenAI→Gemini)
│   ├── langchain_agent.py  # Agent LangChain ReAct
│   ├── langchain_tools.py  # LangChain Tools wrappers
│   ├── tools.py            # search_imt (RAG vectoriel) + send_email
│   ├── vector_search.py    # 🆕 Moteur RAG (Sentence-Transformers)
│   └── __init__.py
├── tests/
│   ├── test_agent.py       # Tests agent classique
│   ├── test_langchain_agent.py  # Tests LangChain
│   └── test_tools.py       # Tests outils
├── memory/
│   └── redis_memory.py     # Mémoire Redis (fallback RAM)
├── data/
│   ├── chunks.json         # 147 paragraphes indexés
│   ├── embeddings.pkl      # 🆕 Embeddings vectoriels (384D)
│   ├── formations.txt      # Contenu formations (94 lignes)
│   ├── contact.txt         # Coordonnées IMT (44 lignes)
│   └── ...                 # 7 fichiers .txt (474 lignes total)
├── scripts/
│   ├── scrape_imt.py       # Scraper site IMT
│   ├── build_index.py      # Découpage paragraphes
│   └── build_vector_index.py # 🆕 Génération embeddings
├── docs/
│   ├── GUIDE_OPENAI.md     # 🆕 Configuration OpenAI
│   ├── GUIDE_LANGFUSE.md   # 🆕 Configuration Langfuse
│   ├── GUIDE_SMTP.md       # Configuration email
│   └── CHECKLIST.md        # Suivi tâches
├── chainlit_app.py         # Interface web Chainlit
├── test_vector_search.py   # 🆕 Tests RAG vectoriel
├── test_agent_rag.py       # 🆕 Tests agent complet
├── requirements.txt        # Dépendances
└── .env                    # Configuration (API keys)
```

## 👥 Équipe & Responsabilités

| Membre | Responsabilités | Statut |
|--------|----------------|--------|
| **Maliki** | Orchestration agent, tools, README, Git, présentation | ✅ Agent + Tools OK, ⏳ README/Git |
| **Makhtar** | Scraping IMT, indexation RAG vectoriel | ✅ Scraping + RAG vectoriel OK |
| **Diabang** | Mémoire Redis, interface Chainlit | ✅ Redis + Chainlit OK, ⏳ UI custom |
| **Debora** | Observabilité Langfuse (traçabilité LLM) | ✅ Code intégré, ⏳ Compte + test |

## 🔧 Développement

### Ajouter une nouvelle fonctionnalité

1. **Créer la fonction** dans `app/tools.py`
2. **Ajouter les tests** dans `tests/test_tools.py`
3. **Mettre à jour l'agent** dans `app/agent.py` si nécessaire
4. **Documenter** dans `docs/`

### Lancer en mode debug

```bash
# Avec logging détaillé
python -c "import logging; logging.basicConfig(level=logging.DEBUG); from app.agent import agent; agent()"
```

### Conventions de code

- **Logging** : Utiliser `logger.info()`, `.warning()`, `.error()`, `.debug()`
- **Tests** : Mocks avec `unittest.mock`, assertions claires
- **Docstrings** : Format Google (Args, Returns, Raises)
- **Validation** : Toujours valider les entrées utilisateur

## 🐛 Troubleshooting

### L'agent ne répond pas
1. Vérifier `GEMINI_API_KEY` dans `.env`
2. Lancer les tests : `pytest tests/test_agent.py`
3. Vérifier les logs

### Email non envoyé
1. Voir le [Guide SMTP](docs/GUIDE_SMTP.md)
2. Vérifier la configuration Gmail (mot de passe d'application)
3. Tester : `python -c "from app.tools import send_email; print(send_email('Test', 'Test'))"`

### Tests échouent
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall

# Vérifier la version Python
python --version  # Doit être 3.11 ou 3.12
```

### Erreurs d'import
```bash
# S'assurer d'être dans l'environnement virtuel
source venv/bin/activate

# Vérifier que le projet est dans PYTHONPATH
export PYTHONPATH=/path/to/imt-agent-clean:$PYTHONPATH
```

## 📊 État du Projet

### Progrès (4/7 jours, 57.1%)

- ✅ **Jour 0** : Préparation, environnement, tests initiaux
- ✅ **Jour 1** : Stabilisation, 22 tests agent, logging
- ✅ **Jour 2** : Email SMTP, validation, 18 tests outils
- ✅ **Jour 3** : Migration LangChain, agent ReAct, 18 tests
- 🔄 **Jour 4** : Intégration Langfuse (en cours de planification)
- ⏳ **Jour 4** : Intégration Langfuse
- ⏳ **Jour 5** : RAG avancé avec embeddings
- ⏳ **Jour 6** : Amélioration UI Chainlit
- ⏳ **Jour 7** : Finalisation et documentation

### Métriques actuelles

- **56 tests** (100% passent)
- **~2000 lignes** de code
- **~1200 lignes** de tests
- **~1000 lignes** de documentation
- **Couverture** : ~91%

## 🤝 Contribution

Ce projet est développé dans le cadre d'un prototype pour l'IMT Sénégal.

### Prochaines fonctionnalités prévues

1. **LangChain** : Migration vers LangChain pour orchestration
2. **Langfuse** : Observabilité et traçabilité des conversations
3. **RAG avancé** : Embeddings vectoriels pour recherche sémantique
4. **UI améliorée** : Upload de documents, historique enrichi
5. **Multi-modal** : Support images et PDF

## 📝 Licence

Projet prototype - Usage interne IMT Sénégal

## 🙏 Remerciements

- **Gemini** pour le LLM
- **Chainlit** pour l'interface
- **pytest** pour les tests
- **Redis** pour la mémoire

---

**Dernière mise à jour** : 23 Janvier 2026  
**Version** : 0.4.0 (Jour 3 complété)  
**Statut** : 🟢 Production-ready avec agent LangChain ReAct
