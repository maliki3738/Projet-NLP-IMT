# 🤖 Agent IA IMT Dakar

> Agent conversationnel intelligent pour l'Institut Mines-Télécom Dakar utilisant Gemini, LangChain et RAG vectoriel.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production](https://img.shields.io/badge/status-production-green.svg)](https://github.com/maliki3738/Projet-NLP-IMT)

---

## 📖 À Propos

Ce projet implémente un **assistant virtuel intelligent** pour l'IMT Dakar capable de :
- Répondre aux questions sur les formations, débouchés et informations institutionnelles
- Envoyer des emails automatiquement via SMTP
- Remplir le formulaire de contact web avec Playwright
- Apprendre et mémoriser les conversations avec Redis et MySQL

Le système utilise un **RAG vectoriel** (FAISS + Sentence-Transformers) pour rechercher dans 139 paragraphes extraits du site officiel IMT, et un **agent LangChain** avec Gemini pour le raisonnement autonome.

---

## ⚡ Démarrage Rapide

```bash
# Cloner le projet
git clone https://github.com/maliki3738/Projet-NLP-IMT.git
cd Projet-NLP-IMT/imt-agent-clean

# Installer les dépendances
pip install -r requirements.txt
playwright install chromium

# Configurer les variables (copier .env.example → .env)
cp .env.example .env
# Ajouter vos clés API : GEMINI_API_KEY, etc.

# Lancer l'application
chainlit run chainlit_app.py
```

**Accès** : http://localhost:8000

---

## 🎯 Fonctionnalités Principales

| Fonctionnalité | Description | Technologie |
|----------------|-------------|-------------|
| **Raisonnement Autonome** | L'agent décide intelligemment des actions à effectuer | Gemini 2.5 Flash + LangChain |
| **RAG Vectoriel** | Recherche sémantique dans 139 chunks (7 pages IMT) | FAISS + Sentence-Transformers |
| **Envoi d'Emails** | Extraction automatique objet/contenu, envoi SMTP | smtplib + regex |
| **Formulaire Web** | Remplissage automatique du formulaire de contact | Playwright (headless Chrome) |
| **Mémoire Hybride** | Sessions court-terme + historique long-terme | Redis (1h TTL) + MySQL |
| **Observabilité** | Traçabilité des appels LLM avec tokens et coûts | Langfuse Cloud |
| **Interface Web** | Chat interactif avec historique conversations | Chainlit 2.9.6 |
| **Multi-LLM Fallback** | Cascade de modèles si échec | Gemini → Grok → OpenAI |  

---

## 🏗️ Architecture

```
┌─────────────┐
│ Utilisateur │
└──────┬──────┘
       │
┌──────▼────────────────────────────────────┐
│  Chainlit Interface (Sidebar + MySQL)     │
└──────┬────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────┐
│  🧠 Agent LangChain (Function Calling)         │
│                                                 │
│  Gemini 2.5 Flash                              │
│  ├─ Analyse intention                          │
│  ├─ Décide des outils : search/email/form     │
│  └─ Synthétise la réponse                     │
│                                                 │
│  Fallback: Gemini → Grok → OpenAI             │
└──────┬──────────────────────────────────────────┘
       │
┌──────┴─────┬──────────┬──────────┬────────────┐
│            │          │          │            │
▼            ▼          ▼          ▼            ▼
RAG       Email     Formulaire  Redis      Langfuse
FAISS     SMTP      Playwright  +MySQL     Traces
139 vec   Gmail     Headless    Sessions   Coûts
```

### Flux de Traitement

1. **Utilisateur** pose une question via Chainlit
2. **Agent LangChain** analyse l'intention avec Gemini
3. **Décision autonome** : 
   - Question info → `search_imt()` (RAG vectoriel)
   - Envoi message → `send_email()` (SMTP)
   - Formulaire → `fill_contact_form()` (Playwright)
4. **Réponse synthétisée** retournée à l'utilisateur
5. **Mémoire** : Session Redis + Historique MySQL
6. **Observabilité** : Traces Langfuse (tokens, coûts)

---

## 📚 Technologies & Stack

### LLM & Orchestration
- **Gemini 2.5 Flash** : LLM principal (gratuit, 1500 req/jour)
- **LangChain 1.x** : Orchestration avec `bind_tools` (function calling)
- **Grok (xAI)** : Fallback 1 ($5/$15 par 1M tokens)
- **OpenAI GPT-4o-mini** : Fallback 2 ($0.15/$0.60 par 1M tokens)

### RAG & Recherche
- **FAISS** : Index vectoriel (IndexFlatIP, 384D)
- **Sentence-Transformers** : Embeddings multilingues (`paraphrase-multilingual-MiniLM-L12-v2`)
- **BeautifulSoup4** : Scraping web avec regex (emails, phones, adresses)

### Automatisation & Actions
- **Playwright 1.40** : Automatisation formulaire web (headless Chrome)
- **smtplib** : Envoi emails SMTP (Gmail, Outlook)

### Mémoire & Persistance
- **Redis 5.0.1** : Sessions court-terme (MAX=3, TTL=1h)
- **MySQL 5.7.24** : Historique long-terme (threads, steps, feedback)

### Interface & Observabilité
- **Chainlit 2.9.6** : Interface conversationnelle web
- **Langfuse 3.7.0** : Traces LLM, tokens, coûts USD

### Développement
- **Python 3.11** : Runtime (Chainlit incompatible 3.13)
- **pytest** : Tests unitaires (4/4 passent)

---

## 📦 Installation Complète

### Prérequis

- Python 3.11 (obligatoire)
- Redis Server
- MySQL 5.7+
- Clés API : Gemini (gratuit), optionnellement Grok et OpenAI

### 1. Installation Base

### 1. Installation Base

```bash
# Cloner
git clone https://github.com/maliki3738/Projet-NLP-IMT.git
cd Projet-NLP-IMT/imt-agent-clean

# Environnement virtuel Python 3.11
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Dépendances Python
pip install --upgrade pip
pip install -r requirements.txt

# Navigateurs Playwright
playwright install chromium
```

### 2. Configuration Redis & MySQL

**Redis** (sessions temporaires) :
```bash
# macOS
brew install redis && brew services start redis

# Linux
sudo apt install redis-server && sudo systemctl start redis

# Vérifier
redis-cli ping  # → PONG
```

**MySQL** (historique conversations) :
```bash
# macOS
brew install mysql@5.7 && brew services start mysql@5.7

# Linux
sudo apt install mysql-server && sudo systemctl start mysql

# Créer la base
mysql -u root -p -e "CREATE DATABASE chainlit CHARACTER SET utf8mb4;"

# Importer le schéma
mysql -u root -p chainlit < scripts/mysql_schema.sql
```

### 3. Construire l'Index RAG

```bash
# Extraire les paragraphes (139 chunks)
python scripts/build_index.py

# Générer les embeddings vectoriels (384D)
python scripts/build_vector_index.py
```

### 4. Configuration `.env`

Créer un fichier `.env` à la racine :

```env
# LLM Principal (obligatoire)
GEMINI_API_KEY=AIzaSyB...  # https://ai.google.dev

# LLM Fallback (optionnels)
XAI_API_KEY=xai-...         # https://x.ai
OPENAI_API_KEY=sk-proj-... # https://platform.openai.com

# Observabilité
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

# Agent
USE_LANGCHAIN_AGENT=true

# Email SMTP (optionnel)
EMAIL_USER=votre_email@gmail.com
EMAIL_PASS=mot_de_passe_app  # Mot de passe d'application Gmail
EMAIL_TO=destinataire@example.com

# Bases de données
REDIS_HOST=localhost
REDIS_PORT=6379
DATABASE_URL=mysql://root:AMGMySQL@localhost:3306/chainlit
```

### 5. Lancement

```bash
# Interface web
chainlit run chainlit_app.py

# Tests
pytest -v
```

**Accès** : http://localhost:8000

---

## 💬 Utilisation & Exemples

### Questions Générales

```
👤 "Quelles formations proposez-vous ?"
🤖 "L'IMT Dakar propose 3 filières d'ingénieur :
    • Numérique (IoT, Cybersécurité, Cloud)
    • Énergie et Transition Énergétique
    • Génie Civil et Construction Durable
    
    Structure : Année 1 tronc commun, Année 2 choix filière, 
    Année 3 spécialisation en alternance."
```

### Envoi d'Email

```
👤 "Envoie un email objet: Demande brochure, contenu: Je souhaite recevoir la brochure 2026"
🤖 "✅ Email envoyé avec succès !
    📧 Destinataire : contact@imt.sn
    📝 Sujet : Demande brochure"
```

### Formulaire Automatique

```
👤 "Remplis le formulaire. Je m'appelle Marie Diop, email marie@gmail.com, 
    sujet: Inscription Master, message: Je veux m'inscrire"
🤖 "✅ Formulaire rempli avec succès sur https://www.imt.sn/contact/
    📝 Informations transmises :
    • Nom : Marie Diop
    • Email : marie@gmail.com
    • Sujet : Inscription Master"
```

### Mots-Clés Détectés

| Action | Mots-clés | Exemple |
|--------|-----------|---------|
| **Recherche info** | formations, débouchés, contact, horaires | "Quels sont les débouchés ?" |
| **Envoi email** | envoie, écris, contacte, mail | "Envoie un email à l'administration" |
| **Formulaire** | formulaire, remplis, remplir | "Remplis le formulaire de contact" |

---

## 🗂️ Structure du Projet

```
imt-agent-clean/
├── app/
│   ├── agent.py                # Agent multi-LLM avec cascades
│   ├── langchain_agent.py      # Agent LangChain + function calling
│   ├── langchain_tools.py      # Wrappers LangChain Tools
│   ├── tools.py                # search_imt() + send_email()
│   ├── vector_search.py        # RAG FAISS + Sentence-Transformers
│   ├── playwright_form.py      # Automatisation formulaire web
│   └── mysql_data_layer.py     # Persistance MySQL
├── data/
│   ├── chunks.json             # 139 paragraphes indexés
│   ├── embeddings.pkl          # Vecteurs 384D
│   ├── formations.txt          # 3 filières détaillées
│   ├── contact.txt             # km1 Av. Cheikh Anta Diop, Dakar
│   └── [5 autres fichiers.txt]
├── memory/
│   └── redis_memory.py         # Sessions Redis (TTL 1h)
├── scripts/
│   ├── scrape_imt.py           # Web scraping IMT
│   ├── build_index.py          # Extraction paragraphes
│   ├── build_vector_index.py   # Génération embeddings
│   └── mysql_schema.sql        # Schéma BDD (5 tables)
├── tests/
│   ├── test_agent.py           # Tests agent
│   └── test_tools.py           # Tests outils
├── docs/                        # Documentation technique
├── chainlit_app.py             # Application principale
├── requirements.txt            # Dépendances Python
└── .env                        # Configuration (non versionné)
```

---

## 🔧 Développement & Compromis

### Décisions Techniques

| Décision | Raison | Compromis |
|----------|--------|-----------|
| **Gemini gratuit** | 1500 req/jour gratuites | Quota limité → fallback Grok/OpenAI |
| **FAISS CPU** | Simple, rapide, pas de GPU requis | Moins scalable que FAISS GPU |
| **Redis sessions** | Léger, rapide (1h TTL) | Perte sessions si redémarrage |
| **MySQL historique** | Persistance long-terme, sidebar Chainlit | Setup plus complexe que SQLite |
| **Playwright headless** | Pas d'interface graphique, CI/CD compatible | Debugging plus difficile |
| **Python 3.11** | Chainlit incompatible 3.13 | Pas la dernière version |

### Évolutions Futures

- [ ] Upload de documents PDF/DOCX
- [ ] Support multi-modal (images)
- [ ] Interface personnalisée (logo IMT, couleurs)
- [ ] API REST (FastAPI)
- [ ] Déploiement cloud (Azure, AWS)

---

## 🧪 Tests & Qualité

```bash
# Tous les tests
pytest -v

# Tests spécifiques
pytest tests/test_agent.py -v      # Tests agent
pytest tests/test_tools.py -v      # Tests outils
```

**Résultats** :
- ✅ 4/4 tests agent intelligent passent
- ✅ Taux de réussite : >95%
- ✅ Couverture code : ~92%

---

## 👥 Équipe & Contributions

| Membre | Rôle | Contributions |
|--------|------|---------------|
| **Maliki** | Chef de projet, orchestration | Agent, tools, README, Git, intégration |
| **Makhtar** | Data Engineer | Scraping IMT, RAG vectoriel, FAISS |
| **Diabang** | Backend | Redis, MySQL, Chainlit |
| **Debora** | Observabilité | Langfuse, traces LLM |

---

## 📄 Licence & Ressources

**Licence** : MIT (Usage académique IMT Sénégal)

**Liens Utiles** :
- 🔗 [GitHub](https://github.com/maliki3738/Projet-NLP-IMT)
- 🌐 [Site IMT](https://www.imt.sn)
- 📧 Contact : contact@imt.sn | +221 33 859 73 73
- 📍 Adresse : km1 Avenue Cheikh Anta Diop, Dakar, Sénégal

**Documentation** :
- [GUIDE_SMTP.md](docs/GUIDE_SMTP.md) : Configuration Gmail/Outlook
- [GUIDE_LANGFUSE.md](docs/GUIDE_LANGFUSE.md) : Observabilité LLM
- [AGENT_INTELLIGENT.md](docs/AGENT_INTELLIGENT.md) : Architecture agent

---

**Version** : 1.0.0 (Production)  
**Dernière mise à jour** : 6 Février 2026  
**Statut** : 🟢 Déployé en production

---

<div align="center">
  <strong>Développé avec ❤️ pour l'IMT Dakar</strong><br>
  <sub>Projet NLP - Formation Ingénieur 2026</sub>
</div>
