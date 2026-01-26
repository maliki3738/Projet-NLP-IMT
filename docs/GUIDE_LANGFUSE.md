# Guide d'activation Langfuse pour IMT Agent

## 🎯 Vue d'ensemble

Langfuse est une plateforme d'observabilité pour applications LLM qui permet de :
- Tracer tous les appels aux modèles (Gemini, Grok, OpenAI)
- Monitorer les coûts et latences
- Analyser les performances des prompts
- Déboguer les conversations

## ⏱️ Temps estimé : 6-7 minutes

## 📋 Prérequis

- ✅ Code déjà intégré dans `app/agent.py`
- ✅ Package `langfuse` installé
- ❌ Compte Langfuse à créer
- ❌ Clés API à récupérer

## 🚀 Étapes d'activation

### Étape 1 : Créer un compte Langfuse (2 minutes)

1. Aller sur : https://cloud.langfuse.com
2. Cliquer sur **Sign Up**
3. S'inscrire avec email (ou GitHub/Google)
4. Confirmer l'email
5. Créer un projet : `imt-agent` (ou autre nom)

**Plan gratuit** : 50 000 événements/mois (largement suffisant)

### Étape 2 : Récupérer les clés API (1 minute)

1. Dans le dashboard Langfuse
2. Aller dans **Settings** (⚙️) → **API Keys**
3. Cliquer sur **Create new API key**
4. Copier les deux clés :
   - `LANGFUSE_PUBLIC_KEY` (commence par `pk-lf-...`)
   - `LANGFUSE_SECRET_KEY` (commence par `sk-lf-...`)

⚠️ **Important** : La clé secrète ne sera affichée qu'une seule fois !

### Étape 3 : Ajouter les clés dans .env (1 minute)

Ouvrir le fichier `.env` et ajouter :

```bash
# Langfuse Observability
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

Sauvegarder le fichier.

### Étape 4 : Tester l'activation (2 minutes)

1. **Redémarrer Chainlit** (pour charger les nouvelles variables) :
   ```bash
   pkill -f chainlit
   ./start_chainlit.sh
   ```

2. **Ou tester directement** :
   ```bash
   python test_agent_rag.py
   ```

3. **Vérifier les logs** - Vous devez voir :
   ```
   ✅ Langfuse configuré avec succès
   ```

   Au lieu de :
   ```
   ⚠️ Langfuse non disponible
   ```

### Étape 5 : Vérifier le dashboard (1 minute)

1. Retourner sur https://cloud.langfuse.com
2. Cliquer sur votre projet `imt-agent`
3. Aller dans l'onglet **Traces**
4. Vous devriez voir les traces des appels LLM :
   - Modèle utilisé (Gemini/Grok/OpenAI)
   - Prompt envoyé
   - Réponse reçue
   - Latence (temps de réponse)
   - Tokens utilisés

**Prendre un screenshot** pour le README !

## 📊 Utilisation du dashboard

### Traces
- Voir tous les appels LLM en temps réel
- Cliquer sur une trace pour voir les détails complets
- Filtrer par modèle, utilisateur, session

### Analytics
- Coûts par modèle
- Latences moyennes
- Tokens utilisés par jour
- Taux d'erreur

### Prompts
- Gérer les versions de prompts
- Comparer les performances
- A/B testing

## ✅ Validation finale

Checklist de vérification :

- [ ] Compte Langfuse créé
- [ ] Clés API dans `.env`
- [ ] Agent redémarré
- [ ] Logs affichent "✅ Langfuse configuré"
- [ ] Dashboard affiche les traces
- [ ] Screenshot pris pour documentation

## 🐛 Dépannage

### Erreur : "Authentication error"
- Vérifier que les clés sont bien copiées (pas d'espaces)
- Vérifier que `LANGFUSE_PUBLIC_KEY` commence par `pk-lf-`
- Vérifier que `LANGFUSE_SECRET_KEY` commence par `sk-lf-`

### Erreur : "No traces in dashboard"
- Attendre 10-30 secondes (délai d'envoi)
- Vérifier que l'agent a bien été appelé (faire une question)
- Vérifier la connexion internet

### Erreur : "Module not found: langfuse"
```bash
source venv/bin/activate
pip install langfuse
```

## 📝 Code intégré (référence)

Le code suivant est déjà dans `app/agent.py` :

```python
# Langfuse initialization
try:
    from langfuse import Langfuse
    langfuse_client = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    LANGFUSE_AVAILABLE = True
    logger.info("✅ Langfuse configuré avec succès")
except Exception as e:
    langfuse_client = None
    LANGFUSE_AVAILABLE = False
    logger.warning(f"⚠️ Langfuse non disponible : {e}")
```

Chaque appel LLM envoie une trace :

```python
if LANGFUSE_AVAILABLE:
    trace = langfuse_client.trace(
        name="gemini_call",
        user_id=session_id,
        metadata={"model": "gemini-pro", "query": query}
    )
```

## 🔗 Ressources

- Documentation Langfuse : https://langfuse.com/docs
- Pricing : https://langfuse.com/pricing (gratuit jusqu'à 50k events)
- Support : support@langfuse.com

## 🎉 Félicitations !

Langfuse est maintenant actif ! Vous pouvez :
- Monitorer toutes les conversations en temps réel
- Analyser les performances des modèles
- Optimiser les coûts
- Déboguer les problèmes efficacement

---

**Prochaine étape** : Customiser l'UI Chainlit (logo, couleurs) → Voir `GUIDE_CHAINLIT.md`
