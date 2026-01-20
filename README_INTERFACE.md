# Agent IMT Dakar - Interface Utilisateur

## 🚀 Démarrage rapide

### Option 1 : Script automatique (recommandé)
Double-cliquez sur `start_app.bat` - cela démarre automatiquement Redis et l'application.

### Option 2 : Démarrage manuel
1. **Démarrer Redis :**
   ```bash
   .\redis\redis-server.exe
   ```

2. **Démarrer l'application :**
   ```bash
   chainlit run chainlit_app.py
   ```

3. **Accéder à l'interface :**
   - Ouvrez votre navigateur à `http://localhost:8000`

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

**Commandes spéciales :**
- `/historique` ou `/history` : Affiche l'historique complet stocké en mémoire

## 🧠 Gestion de l'historique

### Comportement normal :
- **Dans une session** : Chainlit garde automatiquement l'historique visible
- **Entre sessions** : L'historique est stocké dans Redis (ou RAM) pour persistance
- **Pas de duplication** : L'historique ne se répète pas automatiquement au rechargement

### Stockage :
- **Redis disponible** : Historique persistant même après redémarrage de l'app
- **Redis indisponible** : Historique en RAM (perdu au redémarrage)
- **Par session** : Chaque conversation utilisateur est isolée

### Voir l'historique :
Tapez `/historique` pour voir tout l'historique stocké en mémoire.

## �️ Redis - Mémoire persistante

### Installation
Redis est maintenant installé dans le dossier `redis/` du projet.

### Fonctionnement
- **Avec Redis** : Historique persistant même après redémarrage de l'application
- **Sans Redis** : Historique en RAM (perdu au redémarrage)
- **Test** : Au démarrage, vous devriez voir "✅ Redis connecté" dans le terminal

### Dépannage Redis
Si Redis ne démarre pas :
1. Vérifiez qu'aucun autre programme n'utilise le port 6379
2. Redémarrez Redis : `.\redis\redis-server.exe`
3. Testez : `.\redis\redis-cli.exe ping`

## 📝 Notes techniques

- Interface simple et fonctionnelle
- Commentaires dans le code pour compréhension
- Configuration française activée
- Compatible avec/sans Redis