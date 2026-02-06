# 📝 Notes pour la Soutenance - Système de Sessions

## 🏗️ Architecture Dual-Layer

### 1️⃣ **Backend Redis** (Notre système)
- **Limite** : 3 sessions simultanées maximum
- **TTL** : 1 heure (auto-expiration)
- **Utilité** : Gestion mémoire conversationnelle en temps réel
- **Commande** : Tapez `historique` dans le chat pour voir les sessions actives

**Caractéristiques** :
```
✅ Contrôle précis de la mémoire court-terme
✅ Évite la surcharge mémoire (3 max)
✅ Auto-nettoyage après 1h d'inactivité
✅ Parfait pour un chatbot en production
```

### 2️⃣ **Frontend Chainlit + MySQL** (Système natif)
- **Base** : MySQL avec tables Thread, Step, Element
- **Sidebar** : Géré automatiquement par Chainlit UI
- **Utilité** : Historique long-terme et navigation UI

**Caractéristiques** :
```
✅ Tous les messages persistés en base
✅ Historique accessible via sidebar (si disponible)
✅ Recherche et navigation native Chainlit
✅ Aucune limite de stockage
```

## 🎯 Pourquoi cette Architecture ?

### Problème résolu
**Sans Redis** :
- ❌ Toutes les conversations en RAM → crash si trop de sessions
- ❌ Pas de limite de mémoire active
- ❌ Historique infini en mémoire vive

**Avec Redis + TTL** :
- ✅ Seulement 3 conversations "chaudes" en RAM
- ✅ Auto-nettoyage après 1h
- ✅ MySQL conserve tout pour l'historique long-terme

### Analogie Simple
```
Redis    = RAM d'un ordinateur (rapide, limité, volatile)
MySQL    = Disque dur (lent, illimité, permanent)
Chainlit = Interface utilisateur (sidebar, navigation)
```

## 📊 Démonstration pour la Soutenance

### Étape 1 : Montrer la limite Redis
1. Ouvrir 3 onglets → 3 sessions créées
2. Ouvrir un 4ème → La plus ancienne est supprimée automatiquement
3. Dans les logs : `⚠️ Session xxx supprimée (limite de 3 atteinte)`

### Étape 2 : Commande historique
Taper dans le chat : **`historique`**

Résultat :
```
📊 Sessions actives (Backend Redis)

Limite : 3 sessions simultanées
TTL : 60 minutes

Session 1 ✅ Actuelle
- ID : 8e1f7616-1b2...
- Messages : 5
- Expire dans : 58 min

Session 2
- ID : fdb8048d-a3f...
- Messages : 2
- Expire dans : 59 min
```

### Étape 3 : Persistence MySQL
1. Fermer le navigateur
2. Relancer Chainlit
3. Toutes les discussions précédentes sont disponibles en base
4. Le sidebar Chainlit (si actif) montre l'historique complet

## 🎤 Discours de Soutenance (30 secondes)

> "Nous avons implémenté une architecture de sessions à deux niveaux :
> 
> **Backend Redis** pour gérer la mémoire court-terme avec une limite intelligente de 3 sessions simultanées et un TTL d'1 heure. Cela évite la surcharge mémoire en production.
> 
> **MySQL** pour la persistence long-terme via le data layer Chainlit. Tous les messages sont conservés en base et le sidebar natif permet de naviguer dans l'historique.
> 
> Cette approche dual-layer combine les avantages de la rapidité (Redis) et de la durabilité (MySQL), tout en respectant les contraintes d'un système de production."

## 🔧 Commandes Utilisateur

| Commande | Résultat |
|----------|----------|
| `historique` | Affiche les 3 sessions Redis actives |
| `mes discussions` | Alias de `historique` |
| `sessions` | Alias de `historique` |

## 📈 Métriques Techniques

**Redis** :
- MAX_SESSIONS = 3
- SESSION_TTL = 3600 secondes (1h)
- Structure : chat_history:{uuid} → Liste de messages
- Connexion : localhost:6379

**MySQL** :
- DATABASE_URL = mysql://root:AMGMySQL@localhost:3306/chainlit
- Tables : User, Thread, Step, Element, Feedback
- Driver : aiomysql (async)

**LLM** :
- Modèle : Gemini 2.5 Flash (Free Tier)
- Fallback : format_response() si quota épuisé
- Traces : Langfuse (désactivé temporairement)

## ✅ Points Forts pour la Soutenance

1. **Architecture réfléchie** : Dual-layer Redis + MySQL
2. **Production-ready** : Limite de sessions pour éviter crash
3. **UX transparente** : Commande `historique` simple
4. **Scalable** : Séparation mémoire court-terme / long-terme
5. **Documenté** : Code commenté et logs explicites

## ⚠️ Limitations Connues (à mentionner si interrogé)

1. **Sidebar Chainlit** : Dépend du système natif, pas de contrôle direct
2. **Quota Gemini** : Limité en Free Tier, fallback automatique actif
3. **Redis local** : Nécessite serveur Redis actif (facilement conteneurisable)

## 🎯 Conclusion

Le système est **stable, documenté et démontrable**. L'architecture dual-layer montre une compréhension mature des contraintes de production (mémoire, persistence, scalabilité).

**Message clé** : "Nous avons séparé la logique métier (Redis) de la logique UI (Chainlit), ce qui rend le système modulaire et maintenable."
