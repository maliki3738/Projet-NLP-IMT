# 🤖 IMT AI Agent - Agent Conversationnel Intelligent

Agent conversationnel pour l'**Institut des Métiers du Tertiaire (IMT) de Dakar** avec capacités de recherche et d'action.

## 📋 Fonctionnalités

- ✅ **Recherche (RAG)** : Répond aux questions sur l'IMT (formations, frais, localisation, etc.)
- ✅ **Actions** : Envoie des emails de contact au directeur
- ✅ **Mémoire** : Historique des conversations (Redis avec fallback RAM)
- ✅ **Interface** : Chat web interactif avec Chainlit
- 🔄 **Observabilité** : Monitoring avec Langfuse (à venir)

---

## 🛠️ Stack Technique

| Composant | Technologie | Statut |
|-----------|-------------|--------|
| **LLM** | Gemini (Google) | ✅ Opérationnel (SDK 0.8.6) |
| **Orchestration** | Agent maison → LangChain (J3) | 🔄 Migration prévue |
| **Interface** | Chainlit 1.1.301 | ✅ Prêt |
| **Mémoire** | Redis 5.0.1 | ✅ Avec fallback RAM |
| **RAG** | Indexation textuelle → Embeddings (J5) | 🔄 À améliorer |
| **Observabilité** | Langfuse (J4) | ⏳ À venir |
| **Tests** | Pytest | ✅ 2 tests passent |

---

## 🚀 Installation

### Prérequis
- Python 3.11 ou 3.12 (⚠️ Chainlit incompatible avec 3.13)
- Redis (optionnel, fallback RAM disponible)

### 1. Cloner et préparer l'environnement
```bash
cd /chemin/vers/imt-agent-clean
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configuration
Copier `.env.example` vers `.env` et remplir vos clés API :

```bash
cp .env.example .env
# Éditer .env avec vos clés
```

**Variables obligatoires** :
```env
GEMINI_API_KEY=votre_cle_api_gemini_ici
```

**Variables optionnelles (pour email réel)** :
```env
EMAIL_USER=votre_email@gmail.com
EMAIL_PASS=mot_de_passe_application
EMAIL_TO=directeur@imt.sn
```

---

## 💻 Utilisation

### Mode Terminal (Agent simple)
```bash
python -m app.agent
# Pose tes questions à l'agent
```

### Mode Interface Chainlit
```bash
chainlit run chainlit_app.py
# Ouvre automatiquement http://localhost:8000
```

### Lancer les tests
```bash
pytest tests/ -v
```

---

## 📂 Structure du Projet

```
imt-agent-clean/
├── app/
│   ├── agent.py          # Agent principal avec décision SEARCH/EMAIL
│   └── tools.py          # Outils: search_imt, send_email
├── data/
│   ├── *.txt             # Données brutes IMT
│   └── chunks.json       # Index des chunks pour RAG
├── memory/
│   └── redis_memory.py   # Gestion mémoire Redis
├── scripts/
│   ├── scrape_imt.py     # Scraper du site IMT
│   └── build_index.py    # Indexation des données
├── tests/
│   └── test_tools.py     # Tests unitaires
├── docs/
│   ├── PLAN_DEVELOPPEMENT.md   # Plan 7 jours
│   ├── RAPPORT_JOUR0.md        # Rapport de préparation
│   └── CHECKLIST.md            # Check-list complète
├── chainlit_app.py       # Interface Chainlit
├── requirements.txt      # Dépendances Python
├── .env.example          # Template de configuration
└── README.md             # Ce fichier
```

---

## 🎯 Commandes Utiles

### Tests
```bash
# Tous les tests
pytest

# Tests avec verbosité
pytest -v

# Test spécifique
pytest tests/test_tools.py::test_search_imt_non_empty
```

### Réindexation des données
```bash
# Scraper le site IMT
python scripts/scrape_imt.py

# Construire l'index
python scripts/build_index.py
```

### Redis (optionnel)
```bash
# Démarrer Redis
redis-server

# Test de connexion
python test_redis.py
```

---

## 📝 État Actuel (Jour 0 - 23 Jan 2026)

### ✅ Ce qui fonctionne
- Agent répond aux questions basiques
- Recherche dans les données IMT
- Email en mode simulation (ou réel si configuré)
- Mémoire conversationnelle avec Redis
- Tests unitaires passent
- Interface Chainlit prête

### ⚠️ Limitations actuelles
- **SDK Gemini deprecated** : Utilise `google-generativeai 0.8.6` (warning à chaque lancement)
- **RAG basique** : Compte de mots simple, pas d'embeddings sémantiques
- **Pas de LangChain** : Agent "maison" fonctionnel mais basique
- **Pas d'observabilité** : Langfuse pas encore intégré

### 🔄 Améliorations prévues (J1-J7)
- **Jour 1** : Gestion d'erreurs + Tests enrichis
- **Jour 2** : Email réel testé
- **Jour 3** : Migration vers LangChain (résout conflit Pydantic)
- **Jour 4** : Intégration Langfuse
- **Jour 5** : RAG avancé avec embeddings
- **Jour 6** : Interface Chainlit améliorée
- **Jour 7** : Finalisation et remise

---

## 🐛 Problèmes Connus

### Conflit Pydantic
**Problème** : `google-genai` (nouveau SDK) nécessite Pydantic v2, mais Chainlit 1.1.301 nécessite Pydantic v1.

**Solution temporaire** : Utilisation de `google-generativeai 0.8.6` (deprecated).

**Solution définitive** : Migration vers LangChain au Jour 3 qui abstrait le LLM et gère mieux les dépendances.

### Warning Gemini
Le warning "deprecated package" est normal et non bloquant :
```
FutureWarning: All support for the `google.generativeai` package has ended.
```
Il disparaîtra après migration vers LangChain.

---

## 📚 Documentation

- [Plan de Développement](docs/PLAN_DEVELOPPEMENT.md) : Roadmap détaillée 7 jours
- [Rapport Jour 0](docs/RAPPORT_JOUR0.md) : Rapport de préparation
- [Check-list](docs/CHECKLIST.md) : Suivi des tâches

---

## 🤝 Contribution

Ce projet est un prototype éducatif. Pour contribuer :

1. Créer une branche pour votre feature
2. Ajouter des tests pour vos modifications
3. Vérifier que tous les tests passent
4. Documenter vos changements

---

## 📄 Licence

Projet éducatif - IMT Dakar

---

## 🆘 Support

En cas de problème :
1. Vérifier [docs/RAPPORT_JOUR0.md](docs/RAPPORT_JOUR0.md)
2. Consulter les tests : `pytest -v`
3. Vérifier les variables d'environnement dans `.env`
4. Consulter les logs de l'agent

---

*Dernière mise à jour : 23 Janvier 2026*
*Version : 0.1.0 (Jour 0)*
