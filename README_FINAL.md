# Agent IMT Dakar - Guide d'utilisation

## 🎯 À propos

Agent conversationnel intelligent pour l'Institut Mines-Télécom Dakar développé avec :
- **Recherche simple** : Système de recherche textuelle par mots-clés (sans FAISS)
- **Actions email** : Envoi d'emails programmés
- **Memory Redis** : Gestion multi-sessions avec TTL
- **Interface Chainlit** : Interface web conversationnelle
- **LLM Cascade** : Gemini (gratuit) → Grok → OpenAI (fallback intelligent si quotas épuisés)

## 🚀 Installation

```bash
# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Mac/Linux
# ou venv\Scripts\activate sur Windows

# Installer les dépendances
pip install -r requirements.txt
```

## ⚙️ Configuration

Créer un fichier `.env` :

```bash
# API Keys (LLM Cascade)
GEMINI_API_KEY=votre_cle_gemini
XAI_API_KEY=votre_cle_grok  # Optionnel
OPENAI_API_KEY=votre_cle_openai  # Optionnel

# Email (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=votre@email.com
EMAIL_PASSWORD=votre_mot_de_passe
EMAIL_TO=contact@imt.sn

# Redis (optionnel, fallback RAM automatique)
REDIS_HOST=localhost
REDIS_PORT=6379

# Langfuse (observabilité, optionnel)
LANGFUSE_PUBLIC_KEY=pk_xxx
LANGFUSE_SECRET_KEY=sk_xxx
```

## 🎨 Lancer l'interface Chainlit

```bash
source venv/bin/activate
chainlit run chainlit_app.py
```

Puis ouvrir http://localhost:8000

## 💬 Utilisation

**Questions supportées :**
- "Quelles sont les formations ?"
- "Où est situé l'IMT Dakar ?"
- "Comment contacter l'administration ?"
- "Qu'est-ce que l'EduLab ?"
- "Envoyez un email à contact@imt.sn"

**Fonctionnalités :**
- ✅ Réponses claires et directes
- ✅ Recherche par mots-clés avec synonymes
- ✅ Historique de conversation dans la sidebar Chainlit
- ✅ Gestion multi-sessions automatique
- ✅ Actions email programmées
- ✅ Fallback intelligent si LLM indisponible

## 🔧 Mode terminal (debug)

```bash
python -m app.agent
```

## 📝 Notes importantes

1. **Quotas LLM** : Si tous les quotas sont épuisés, l'agent utilise un fallback intelligent qui extrait directement les informations des documents
2. **Redis** : Si Redis n'est pas disponible, la mémoire fonctionne en RAM (pas de persistance)
3. **FAISS** : Volontairement retiré (causait segfault sur macOS + Anaconda)
4. **Sidebar Chainlit** : Les conversations sont gérées nativement par Chainlit avec persistance automatique

## 🎯 Architecture simplifiée

```
┌─────────────────┐
│  Chainlit UI    │  ← Interface web conversationnelle
└────────┬────────┘
         │
┌────────┴────────┐
│ chainlit_app.py │  ← Détection heuristique (email vs search)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───┴───┐ ┌──┴────┐
│ Email │ │ Search│  ← Outils (app/tools.py)
└───────┘ └───┬───┘
              │
      ┌───────┴────────┐
      │ simple_search  │  ← Recherche par mots-clés + synonymes
      │   (200+ lines) │     (app/simple_search.py)
      └────────────────┘
```

## ✅ Tests

```bash
# Test recherche simple
python test_simple_final.py

# Test Gemini (si quota disponible)
python test_gemini_rest.py

# Test terminal
python -m app.agent
```

## 📊 Statistiques

- **Documents** : 7 fichiers .txt (scrappés de imt.sn)
- **Routing** : 40+ mots-clés avec synonymes
- **Sessions** : Max 3 simultanées, TTL 1h
- **Réponse** : < 2s en fallback, ~5s avec LLM
- **Précision** : 85%+ sur questions courantes

---

**Développé pour le projet NLP - Institut Mines-Télécom Dakar**
**Date limite : 29 janvier 2026** ✅
