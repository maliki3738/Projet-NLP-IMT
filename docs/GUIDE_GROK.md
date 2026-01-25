# 🚀 Guide Rapide : Utiliser Grok (xAI)

## Pourquoi Grok ?

Si tu as atteint le quota gratuit de Gemini, Grok de xAI est une excellente alternative temporaire.

## 📝 Étapes d'installation

### 1️⃣ Obtenir ta clé API Grok

1. Va sur **https://console.x.ai/**
2. Connecte-toi avec ton compte X/Twitter
3. Clique sur **"API Keys"** dans le menu
4. Clique sur **"Create API Key"**
5. Copie la clé (tu ne pourras la voir qu'une fois !)

### 2️⃣ Ajouter la clé dans .env

Ouvre ton fichier `.env` et ajoute :

```bash
# Grok (xAI) - Alternative à Gemini
XAI_API_KEY=xai-xxxxxxxxxxxxxxxxxxxxxxxxxx
```

**OU** si tu préfères :

```bash
GROK_API_KEY=xai-xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3️⃣ Redémarrer Chainlit

```bash
pkill -9 -f chainlit
cd /Users/mac/Desktop/NLP/Projet/imt-agent-clean
source venv/bin/activate
USE_LANGCHAIN_AGENT=false chainlit run chainlit_app.py -w
```

## ✅ Vérification

Tu devrais voir dans les logs au démarrage :

```
✅ Grok (xAI) configuré avec succès
🚀 Utilisation de Grok comme LLM principal
```

## 🔄 Retour à Gemini

Quand ton quota Gemini se réinitialisera (généralement après 24h), tu peux :

1. **Option 1** : Garder les deux clés → L'agent utilisera Grok en priorité puis Gemini en fallback
2. **Option 2** : Supprimer `XAI_API_KEY` du `.env` → Retour automatique à Gemini

## 📊 Comparaison

| LLM | Quota gratuit | Vitesse | Notes |
|-----|---------------|---------|-------|
| **Grok** | Généreux | 🚀 Rapide | API compatible OpenAI |
| **Gemini** | Limité | ⚡ Très rapide | Quota atteint actuellement |

## 🐛 Dépannage

**Erreur "Invalid API Key"** :
- Vérifie que la clé commence par `xai-`
- Vérifie qu'il n'y a pas d'espaces avant/après dans le `.env`

**Grok ne répond pas** :
- Vérifie ta connexion internet
- L'API xAI pourrait être temporairement indisponible
- L'agent basculera automatiquement sur le fallback heuristique

## 💡 Astuce

Le code garde **_call_gemini()** comme nom de fonction, mais appelle Grok en premier si disponible. Pas besoin de changer le code existant !
