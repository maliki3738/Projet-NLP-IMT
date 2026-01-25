# 🤖 Guide d'utilisation OpenAI GPT

## ✅ Configuration rapide (5 minutes)

### Étape 1 : Créer un compte OpenAI
1. Aller sur https://platform.openai.com/signup
2. Créer un compte (email + vérification)
3. Accepter les conditions d'utilisation

### Étape 2 : Ajouter du crédit
1. Aller sur https://platform.openai.com/settings/organization/billing/overview
2. Cliquer sur **"Add payment method"**
3. Ajouter une carte bancaire
4. Acheter **5$ de crédits** (minimum requis)
   - ⚠️ Note : Ton usage réel sera ~0.04$ à 0.32$ pour 1 semaine
   - Le reste des crédits reste disponible plusieurs mois

### Étape 3 : Générer une clé API
1. Aller sur https://platform.openai.com/api-keys
2. Cliquer sur **"Create new secret key"**
3. Donner un nom : `IMT-Agent`
4. Copier la clé (elle commence par `sk-proj-...`)
   - ⚠️ **IMPORTANT** : Tu ne pourras plus la revoir, sauvegarde-la !

### Étape 4 : Configurer dans `.env`
```bash
# Ouvrir le fichier .env
nano .env

# Ajouter ta clé (remplacer YOUR_KEY par ta vraie clé)
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Étape 5 : Tester
```bash
# Relancer l'agent
python3 -c "from app.agent import agent; print(agent('C\'est quoi l\'IMT?'))"
```

---

## 💰 Coûts détaillés

### Modèle utilisé : **GPT-4o-mini**
- Le moins cher d'OpenAI
- Parfait pour reformulation de texte
- Largement suffisant pour ton usage

### Tarifs
- **Entrée** : 0.15 $/1M tokens
- **Sortie** : 0.60 $/1M tokens

### Estimation pour 1 semaine
| Usage | Questions/jour | Coût total |
|-------|---------------|------------|
| **Léger** | 30 | **0.04$** ✅ |
| **Moyen** | 50 | **0.06$** |
| **Intensif** | 100 | **0.13$** |

---

## 🔄 Ordre de priorité des LLMs

L'agent essaie dans cet ordre :
1. **Grok** (xAI) - si configuré et crédits disponibles
2. **OpenAI GPT** - économique et fiable ✅
3. **Gemini** (Google) - gratuit mais quota limité
4. **Fallback** - extraction brute si tous échouent

---

## 🆘 Problèmes courants

### Erreur : "Incorrect API key provided"
- ✅ Vérifie que tu as bien copié toute la clé (commence par `sk-proj-`)
- ✅ Vérifie qu'il n'y a pas d'espaces avant/après dans `.env`

### Erreur : "You exceeded your current quota"
- ✅ Vérifie que tu as ajouté des crédits sur ton compte
- ✅ Attends quelques minutes après l'achat (synchronisation)

### Erreur : "Rate limit exceeded"
- ✅ Tu envoies trop de requêtes trop vite
- ✅ Attends 1-2 secondes entre les questions

---

## 📊 Suivre ta consommation

1. Aller sur https://platform.openai.com/usage
2. Tu verras :
   - Nombre de requêtes
   - Tokens utilisés
   - Coût exact en temps réel

---

## 🎯 Résumé

**Pour 5$ d'achat initial** :
- ✅ ~0.10$ d'utilisation réelle pour 1 semaine
- ✅ Reste 4.90$ pour les mois suivants
- ✅ Réponses de qualité avec GPT-4o-mini
- ✅ Fallback automatique si problème

**Rentable et fiable !** 🚀
