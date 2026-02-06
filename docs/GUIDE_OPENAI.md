# 🤖 Configuration OpenAI GPT - Fallback LLM

> OpenAI GPT-4o-mini comme 3ème fallback après Gemini et Grok.

---

## Configuration Rapide

### 1. Créer Compte OpenAI

1. S'inscrire : https://platform.openai.com/signup
2. Vérifier l'email
3. Accepter les conditions

### 2. Ajouter Crédit

1. Aller sur https://platform.openai.com/settings/organization/billing/overview
2. **Add payment method** (carte bancaire)
3. Acheter **5$** minimum (usage réel ~$0.10/semaine)

### 3. Générer Clé API

1. Aller sur https://platform.openai.com/api-keys
2. **Create new secret key**
3. Nom : `IMT-Agent`
4. Copier la clé `sk-proj-...`

⚠️ **Important** : La clé ne s'affiche qu'une fois !

### 4. Configuration `.env`

```env
# OpenAI GPT (fallback 2)
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

## Coûts

**Modèle** : GPT-4o-mini (le moins cher)

| Usage | Tokens | Coût |
|-------|--------|------|
| Entrée | 1M | $0.15 |
| Sortie | 1M | $0.60 |

**Estimation 1 semaine** :
- 100 requêtes × ~200 tokens = 20k tokens
- Coût : ~$0.02 entrée + $0.01 sortie = **$0.03/semaine**

---

## Test

```bash
# Test agent avec fallback OpenAI
python -c "from app.agent import agent; print(agent('Test OpenAI'))"

# Vérifier logs
# Si Gemini et Grok échouent : "🤖 Tentative OpenAI..."
```

---

## Cascade de Fallback

```
1. Gemini 2.5 Flash (gratuit, 1500 req/jour)
   ↓ échec
2. Grok (xAI, $5/$15 par 1M)
   ↓ échec
3. OpenAI GPT-4o-mini ($0.15/$0.60 par 1M)  ← Vous êtes ici
   ↓ échec
4. Heuristique simple (keywords)
```

---

**Documentation** : [app/agent.py](../app/agent.py) (fonction `_call_openai`)
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
