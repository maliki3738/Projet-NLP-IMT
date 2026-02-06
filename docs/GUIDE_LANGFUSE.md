# 📊 Configuration Langfuse - Observabilité LLM

> Plateforme d'observabilité pour tracer les appels LLM, monitorer les coûts et analyser les performances.

---

## Création Compte (2 minutes)

1. Aller sur https://cloud.langfuse.com
2. **Sign Up** avec email/GitHub/Google
3. Confirmer l'email
4. Créer un projet : `imt-agent`

**Plan gratuit** : 50 000 événements/mois

---

## Récupération Clés API (1 minute)

1. Dashboard Langfuse → **Settings** ⚙️ → **API Keys**
2. **Create new API key**
3. Copier les 2 clés :
   - `LANGFUSE_PUBLIC_KEY` (pk-lf-...)
   - `LANGFUSE_SECRET_KEY` (sk-lf-...)

⚠️ La clé secrète ne s'affiche qu'une fois !

---

## Configuration `.env`

```env
# Langfuse Observability
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## Test

```bash
# Redémarrer Chainlit
chainlit run chainlit_app.py

# Vérifier logs
# ✅ "Langfuse configuré avec succès"
# au lieu de ⚠️ "Langfuse non disponible"
```

---

## Dashboard Langfuse

**Accès** : https://cloud.langfuse.com → Projet `imt-agent`

### Onglets Disponibles

| Onglet | Information |
|--------|-------------|
| **Traces** | Tous les appels LLM en temps réel |
| **Analytics** | Statistiques tokens, coûts, latences |
| **Prompts** | Historique des prompts utilisés |
| **Users** | Sessions utilisateurs |

### Exemple de Trace

```json
{
  "model": "gemini-2.5-flash",
  "tokens_input": 125,
  "tokens_output": 89,
  "cost_usd": 0.0,
  "latency_ms": 1200,
  "status": "success"
}
```

---

## Données Trackées

```python
# Code dans app/agent.py
langfuse_client.create_event(
    name="gemini_response",
    metadata={
        "model": "gemini-2.5-flash",
        "tokens_input": input_tokens,
        "tokens_output": output_tokens,
        "cost_usd": 0.0  # Gemini gratuit
    },
    input=prompt[:500],
    output=result[:500]
)
```

**Metrics** :
- Tokens input/output
- Coûts USD (Grok, OpenAI)
- Latence (ms)
- Taux d'erreur

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Clés invalides | Vérifier copié/collé sans espaces |
| Pas de traces | Redémarrer app après config .env |
| Dashboard vide | Tester avec `python test_agent_rag.py` |

---

**Documentation** : [app/agent.py](../app/agent.py) (lignes 340-360)
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
