📋 **INSTRUCTIONS FINALES - Configuration Grok**

## 🎯 Étapes à suivre MAINTENANT :

### 1️⃣ Obtenir ta clé API Grok (5 minutes)

1. Ouvre un navigateur et va sur : **https://console.x.ai/**
2. Connecte-toi avec ton compte X/Twitter
3. Dans le menu de gauche, clique sur **"API Keys"**
4. Clique sur **"Create API Key"**
5. **COPIE** la clé immédiatement (format : `xai-xxxxxxxxxxxxxxx`)

### 2️⃣ Ajouter la clé dans ton .env

Ouvre le fichier `.env` dans VS Code et ajoute cette ligne APRÈS les clés Gemini :

```bash
# Grok (xAI) - Alternative temporaire à Gemini
XAI_API_KEY=xai-COLLE_TA_CLE_ICI
```

**Exemple :**
```bash
GEMINI_API_KEY=AIzaSyDTVSrsUfylRKmUnU40Q9fCadDKmYePcLY
GOOGLE_API_KEY=AIzaSyDTVSrsUfylRKmUnU40Q9fCadDKmYePcLY

# Grok (xAI) - Alternative temporaire à Gemini  
XAI_API_KEY=xai-Dx8kL9mP3nQr7sT1vW4yZ2aC5bH8jK0f
```

### 3️⃣ Redémarrer Chainlit

Dans le terminal VS Code, exécute :

```bash
pkill -9 -f chainlit && sleep 2
cd /Users/mac/Desktop/NLP/Projet/imt-agent-clean
source venv/bin/activate
USE_LANGCHAIN_AGENT=false chainlit run chainlit_app.py -w
```

### 4️⃣ Vérifier que ça fonctionne

Tu devrais voir dans le terminal :

```
✅ Grok (xAI) configuré avec succès
✅ Redis connecté - historique persistant disponible
Your app is available at http://localhost:8000
```

## ✅ Test rapide

Va sur http://localhost:8000 et pose une question :

```
Toi: C'est quoi l'IMT Dakar ?
```

Si tu vois une réponse claire et bien formulée (pas juste du texte brut), **Grok fonctionne !** 🎉

## 🔧 Si ça ne marche pas

**Erreur "Invalid API Key"** :
- Vérifie que la clé commence bien par `xai-`
- Pas d'espaces avant/après dans le `.env`
- Redemarre Chainlit

**Aucun message d'erreur mais réponses basiques** :
- C'est normal, le fallback heuristique fonctionne
- Grok n'est peut-être pas activé
- Vérifie que `XAI_API_KEY` est bien dans `.env`

## 📚 Documentation complète

Consulte `docs/GUIDE_GROK.md` pour plus de détails.

---

## ⏰ Estimation

- Obtenir clé API : **2 minutes**
- Configurer .env : **1 minute**  
- Tester : **2 minutes**

**TOTAL : ~5 minutes** ⚡
