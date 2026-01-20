# Agent IMT Dakar - Interface Utilisateur

## 🚀 Démarrage rapide

1. **Lancer l'application :**
   ```bash
   chainlit run chainlit_app.py
   ```

2. **Accéder à l'interface :**
   - Ouvrez votre navigateur à `http://localhost:8000`
   - L'interface s'affiche en français

## 🤖 Fonctionnalités

### Interface Chat
- **Agent intelligent** spécialisé dans les informations IMT Dakar
- **Mémoire de conversation** persistante (Redis ou RAM)
- **Décisions automatiques** : recherche d'infos vs envoi d'email

### Mémoire
- **Redis** : historique persistant entre redémarrages
- **Fallback RAM** : fonctionne même sans Redis
- **Par session** : conversations isolées

## 💬 Utilisation

Posez des questions comme :
- "Quels sont les frais de scolarité ?"
- "Comment contacter le directeur ?"
- "Quelles formations proposez-vous ?"

L'agent garde le contexte de la conversation !

## 🛠️ Architecture

- `chainlit_app.py` : Interface utilisateur et gestion des messages
- `memory/redis_memory.py` : Gestion de la mémoire avec fallback
- `app/agent.py` : Logique de décision et traitement
- `app/tools.py` : Outils de recherche et d'email

## 📝 Notes techniques

- Interface simple et fonctionnelle
- Commentaires dans le code pour compréhension
- Configuration française activée
- Compatible avec/sans Redis