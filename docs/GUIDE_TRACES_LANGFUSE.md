# 📊 Guide d'Observabilité : Traces et Coûts avec Langfuse

## ✅ Configuration Actuelle

Votre application est **déjà configurée** avec Langfuse pour tracer tous les appels LLM.

### Clés configurées dans `.env` :
```bash
LANGFUSE_SECRET_KEY=sk-lf-5a00cf24-8fdf-4aab-861a-e010321a3af2
LANGFUSE_PUBLIC_KEY=pk-lf-e7eb29d7-1e12-4f24-8048-e70d7ec07962
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

## 🔍 Comment Voir les Traces et Coûts ?

### 1️⃣ Accéder au Dashboard Langfuse

🌐 **URL** : https://cloud.langfuse.com

📧 **Connexion** : Utilisez votre compte Langfuse (celui associé aux clés ci-dessus)

### 2️⃣ Ce Que Vous Verrez

Une fois connecté, vous aurez accès à :

#### 📈 **Dashboard Principal**
- **Nombre total de requêtes** par jour/semaine
- **Coûts cumulés** en USD
- **Latence moyenne** des réponses
- **Taux d'erreur**

#### 🔎 **Traces Détaillées**
Pour chaque requête utilisateur, vous verrez :
- **Input** : La question posée
- **Output** : La réponse générée
- **Modèle utilisé** : `gemini-2.5-flash`, `grok-beta`, ou `gpt-4o-mini`
- **Tokens utilisés** :
  - Prompt tokens (entrée)
  - Completion tokens (sortie)
  - Total tokens
- **Coût** : Prix exact de la requête (en USD)
- **Latence** : Temps de réponse
- **Timestamp** : Date et heure exactes

#### 💰 **Analyse des Coûts par Modèle**

**Gemini 2.5 Flash (Actuel)** :
- ✅ **GRATUIT** (Free Tier)
- Coût : **0.00 USD** par requête
- Limite : 15 requêtes/minute
- Idéal pour usage modéré

**OpenAI GPT-4o-mini** (Si activé) :
- 💵 Input : 0.15$/1M tokens
- 💵 Output : 0.60$/1M tokens
- Coût moyen : ~0.0001-0.0005 USD par requête
- Nécessite 5$ de crédits minimum

**Grok Beta** (xAI) :
- 💵 Input : 5$/1M tokens
- 💵 Output : 15$/1M tokens
- Coût moyen : ~0.001-0.003 USD par requête
- Plus cher, mais très performant

## 📊 Exemple de Trace Langfuse

```
┌─────────────────────────────────────────────────┐
│ Trace ID: abc-123-def                           │
├─────────────────────────────────────────────────┤
│ Timestamp: 2026-02-05 20:15:32                  │
│ Model: gemini-2.5-flash                         │
├─────────────────────────────────────────────────┤
│ INPUT (Prompt):                                 │
│   "Quelles formations propose l'IMT Dakar ?"    │
├─────────────────────────────────────────────────┤
│ OUTPUT (Response):                              │
│   "L'IMT Dakar propose plusieurs formations..." │
├─────────────────────────────────────────────────┤
│ USAGE:                                          │
│   • Prompt tokens: 234                          │
│   • Completion tokens: 156                      │
│   • Total: 390 tokens                           │
├─────────────────────────────────────────────────┤
│ COST: $0.00 (Free Tier)                         │
│ LATENCY: 1.2s                                   │
└─────────────────────────────────────────────────┘
```

## 🎯 Fonctionnalités Utiles de Langfuse

### 1. **Filtrage par Modèle**
Voir uniquement les traces de `gemini-2.5-flash`, `grok-beta`, ou `gpt-4o-mini`

### 2. **Filtrage par Date**
Analyser l'usage sur une période spécifique

### 3. **Export des Données**
Télécharger les traces en CSV pour analyse Excel

### 4. **Alertes de Coût**
Configurer des alertes si le coût dépasse un seuil (ex: 5$/jour)

### 5. **Analyse de Qualité**
- Temps de réponse moyen
- Taille des réponses
- Détection d'anomalies

## 🚀 Comment Tester ?

1. **Lancez votre application** :
   ```bash
   chainlit run chainlit_app.py
   ```

2. **Posez quelques questions** dans le chatbot

3. **Allez sur Langfuse** :
   - https://cloud.langfuse.com
   - Cliquez sur "Traces" dans le menu de gauche
   - Vous verrez toutes vos requêtes en temps réel ! 🎉

## 📝 Événements Tracés Automatiquement

Votre application trace automatiquement :

✅ **Appels Gemini** (`gemini_call`)
- Prompt + réponse
- Tokens utilisés
- Coût : 0.00$ (Free)

✅ **Appels OpenAI** (`openai_call`) - Si activé
- Prompt + réponse
- Tokens + coût exact

✅ **Appels Grok** (`grok_call`) - Si activé
- Prompt + réponse
- Tokens + coût exact

✅ **Erreurs LLM** (`gemini_call_error`, etc.)
- Messages d'erreur détaillés
- Timestamp de l'échec

## 💡 Conseils

1. **Surveillez votre quota Gemini** :
   - Free Tier : 15 requêtes/minute
   - Si dépassé, les requêtes échouent pendant 1 minute

2. **Optimisez les coûts** :
   - Gemini 2.5 Flash = **GRATUIT** → Parfait pour votre usage
   - Passez à OpenAI/Grok uniquement si besoin de qualité supérieure

3. **Analysez les patterns** :
   - Questions les plus fréquentes
   - Temps de réponse moyens
   - Heures de pic d'utilisation

## 🔗 Liens Utiles

- 🌐 Dashboard Langfuse : https://cloud.langfuse.com
- 📚 Documentation Langfuse : https://langfuse.com/docs
- 💰 Pricing Gemini : https://ai.google.dev/pricing
- 💰 Pricing OpenAI : https://openai.com/pricing

---

**Statut actuel** :
- ✅ Gemini 2.5 Flash actif (GRATUIT)
- ✅ Langfuse configuré et prêt
- ✅ Toutes les traces sont automatiquement enregistrées
