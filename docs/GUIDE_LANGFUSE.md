# 📊 Guide Langfuse - Observabilité et Traçabilité

## Vue d'ensemble

**Langfuse** est une plateforme d'observabilité pour applications LLM/IA. Elle permet de :

- 🔍 **Tracer** tous les appels LLM (Gemini, etc.)
- 📈 **Monitorer** les performances et les coûts
- 🐛 **Déboguer** les conversations complexes
- 📊 **Analyser** les patterns d'utilisation
- 💰 **Calculer** les coûts par requête/utilisateur

---

## 1️⃣ Configuration Langfuse

### 1.1 Créer un compte (Gratuit)

1. Allez sur : **https://cloud.langfuse.com**
2. Inscrivez-vous (Email + Mot de passe)
3. Plan gratuit : **50,000 événements/mois**

### 1.2 Créer un projet

1. Dashboard → **New Project**
2. Nom : `imt-agent`
3. Cliquez **Create**

### 1.3 Récupérer les clés API

1. Settings (⚙️) → **API Keys**
2. Cliquez **Create new API key**
3. Copiez :
   - 🔑 **Public Key** : `pk-lf-xxxxxxx...`
   - 🔐 **Secret Key** : `sk-lf-xxxxxxx...`

### 1.4 Ajouter au `.env`

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## 2️⃣ Comment ça marche dans le code ?

### Intégration dans l'agent

```python
# Dans app/langchain_agent.py
from langfuse import Langfuse

# Initialisation
langfuse_client = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

# Chaque appel LLM est automatiquement tracé
```

### Qu'est-ce qui est tracé ?

- ✅ Tous les appels à Gemini
- ✅ Entrées/sorties des outils (search_imt, send_email)
- ✅ Étapes intermédiaires de raisonnement
- ✅ Latence et coûts

---

## 3️⃣ Utiliser le Dashboard

### Dashboard Langfuse

| Onglet | Utilité |
|--------|---------|
| **Traces** | Voir tous les appels LLM avec détails |
| **Analytics** | Graphiques de performance et coûts |
| **Issues** | Appels qui ont échoué ou sont lents |
| **Settings** | Gérer les clés API et projets |

### Accéder aux traces

1. Login : https://cloud.langfuse.com
2. Projet : `imt-agent`
3. Onglet : **Traces**
4. Vous verrez chaque appel LLM avec :
   - Input/Output
   - Durée d'exécution
   - Coût estimé
   - Timestamp

---

## 4️⃣ Exemples

### Exemple de trace

```
Trace ID: trace-001
Timestamp: 2026-01-26 14:30:00
Duration: 2.5s
Cost: $0.00012

Input: "Quelles sont les formations à l'IMT ?"
Output: "L'IMT propose les formations suivantes..."

Steps:
  1. search_imt() → 0.8s
  2. Gemini reformulation → 1.7s
```

### Voir les coûts

- Settings → **Usage** : Coûts totaux du mois
- Traces → Détail par requête

---

## 5️⃣ Dépannage

### ❌ Pas de traces qui apparaissent ?

**Vérifier :**

```bash
# 1. Clés dans .env
cat .env | grep LANGFUSE

# 2. Test simple
python -c "from langfuse import Langfuse; print('✅ Langfuse OK')"

# 3. Lancer l'agent
python test_agent_rag.py
```

### ❌ Erreur "Clés manquantes" ?

```python
# Dans langchain_agent.py, vous verrez :
logger.warning("⚠️  Clés Langfuse manquantes")
```

**Solution :** Mettez à jour `.env` et relancez.

### ❌ Connexion impossible ?

**Vérifier :**
- Votre connexion internet
- Les clés copient correctement (pas d'espaces)
- Le compte Langfuse est actif

---

## 6️⃣ Cas d'usage courants

### 📊 Analyser la qualité des réponses

1. Dashboard → **Traces**
2. Filtrer par type de question
3. Analyser Input/Output

### 💰 Calculer le coût/utilisateur

1. Dashboard → **Analytics**
2. Grouper par `user_id`
3. Voir coût total

### 🐛 Déboguer une question problématique

1. Dashboard → **Traces**
2. Rechercher par timestamp ou question
3. Voir tous les appels intermédiaires

---

## 7️⃣ Ressources

- 📖 **Documentation officielle** : https://langfuse.com/docs
- 🚀 **SDK Python** : https://github.com/langfuse/langfuse-python
- 💬 **Chat Support** : Dans le dashboard Langfuse

---

## 8️⃣ Étapes suivantes

- [ ] Créer dashboard personnalisé (Analytics)
- [ ] Configurer alertes (Issues)
- [ ] Exporter données pour rapports
- [ ] Intégrer avec Slack/Email pour alertes

---

**✅ Langfuse est maintenant prêt à tracer votre agent IMT !** 🚀

Pour vérifier : lancez `python test_agent_rag.py` et allez voir les traces sur le dashboard.
