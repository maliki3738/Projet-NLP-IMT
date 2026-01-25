# docs/GUIDE_LANGFUSE.md

# 🔍 Guide d'intégration Langfuse

## 📋 Vue d'ensemble

**Langfuse** est une plateforme d'observabilité pour applications LLM (Large Language Models). Elle permet de :
- Tracer tous les appels aux modèles (Grok, OpenAI, Gemini)
- Monitorer les performances (latence, coûts, tokens)
- Débugger les problèmes en production
- Analyser les conversations utilisateurs

---

## 🎯 Étape 1 : Créer un compte Langfuse

1. Aller sur **[https://cloud.langfuse.com](https://cloud.langfuse.com)**
2. S'inscrire gratuitement (plan gratuit : 50k événements/mois)
3. Créer un nouveau projet : `imt-agent`

---

## 🔑 Étape 2 : Récupérer les clés API

Dans votre dashboard Langfuse :

1. Cliquer sur **"Settings"** → **"API Keys"**
2. Créer une nouvelle clé et copier :
   - **Public Key** : `pk-lf-...`
   - **Secret Key** : `sk-lf-...`
   - **Host** : `https://cloud.langfuse.com`

---

## ⚙️ Étape 3 : Configurer le fichier .env

Ajouter ces variables dans `.env` :

```bash
# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## 🔧 Étape 4 : Intégrer dans agent.py

Le code est déjà préparé dans `app/agent.py`. Décommenter les sections Langfuse :

1. **Import** (ligne ~7-10)
2. **Initialisation** (ligne ~40-45)
3. **Traces dans _call_grok()** (ligne ~75-80)
4. **Traces dans _call_openai()** (ligne ~100-105)
5. **Traces dans _call_gemini()** (ligne ~125-130)

---

## ✅ Étape 5 : Tester l'intégration

```bash
python test_agent_simple.py
```

Vérifier sur **[cloud.langfuse.com](https://cloud.langfuse.com)** :
- Onglet **"Traces"** → Voir les appels LLM
- Onglet **"Sessions"** → Analyser les conversations
- Onglet **"Metrics"** → Coûts et performances

---

## 📊 Dashboard Langfuse

Exemple de ce que vous verrez :

```
┌─────────────────────────────────────────────────┐
│ Traces                                          │
├─────────────────────────────────────────────────┤
│ 2026-01-25 19:00:00                            │
│ Question: "Quelles formations proposez-vous ?"  │
│ Model: grok-beta (fallback)                     │
│ Latency: 1.2s                                   │
│ Tokens: 150 input / 80 output                  │
│ Cost: $0.0005                                   │
└─────────────────────────────────────────────────┘
```

---

## 🎓 Bénéfices

✅ **Transparence totale** : Voir tous les appels LLM  
✅ **Débogage facile** : Identifier les erreurs  
✅ **Optimisation coûts** : Tracker dépenses par modèle  
✅ **Amélioration continue** : Analyser qualité réponses  

---

## 🚀 Prochaines étapes

1. Créer compte Langfuse
2. Ajouter clés dans `.env`
3. Décommenter code dans `agent.py`
4. Tester et valider dashboard
5. Documenter dans README.md

**Responsable** : Debora  
**Temps estimé** : 2-3 heures
