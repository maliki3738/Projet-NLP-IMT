# 📋 PLAN DE DÉVELOPPEMENT - Agent IMT
**Période : 23-30 Janvier 2026**

---

## ✅ JOUR 0 (23 Janvier) - PRÉPARATION - ✅ TERMINÉ

### Modifications effectuées :
1. ✅ **Environnement virtuel recréé** : Dépendances propres installées
2. ✅ **Tests corrigés** : Ajout de `sys.path` pour résoudre les imports
3. ✅ **Tests passent** : 2/2 tests réussis
4. ✅ **Agent fonctionnel** : Testé avec succès (utilise google-generativeai 0.8.6)
5. ✅ **Configuration** : Fichier `.env.example` créé
6. ✅ **Documentation** : Plan de développement créé

### ⚠️ Note importante sur Gemini :
- **Conflit de dépendances** : Le nouveau SDK `google-genai` nécessite Pydantic v2, mais Chainlit 1.1.301 nécessite Pydantic v1
- **Solution temporaire** : Utilisation de `google-generativeai 0.8.6` (ancien SDK, deprecated)
- **Solution définitive** : Migration vers LangChain au Jour 3 qui gérera mieux ces conflits

### État actuel :
- ✅ Agent de base fonctionnel (avec fallback heuristique si Gemini absent)
- ✅ Recherche basique opérationnelle
- ✅ Email SMTP codé (non testé avec vrais identifiants)
- ✅ Mémoire Redis avec fallback RAM
- ✅ Interface Chainlit prête
- ⚠️ SDK Gemini deprecated (à migrer via LangChain)
- ⚠️ Pas encore de Langfuse
- ⚠️ RAG basique (comptage de mots)

---

## 📅 JOUR 1 (24 Janvier - 1h) - STABILISATION

### Objectifs :
1. **Améliorer la gestion d'erreurs**
   - Ajouter try/except dans l'agent
   - Logger les erreurs
   - Fallback propres

2. **Enrichir les tests**
   - Test de l'agent complet
   - Test des cas d'erreur
   - Mock de Gemini pour tests offline

3. **Améliorer la recherche**
   - Gérer les questions mal formées
   - Améliorer les heuristiques

### Fichiers à modifier :
- `app/agent.py` : Gestion d'erreurs
- `tests/test_tools.py` : Nouveaux tests
- `tests/test_agent.py` : Nouveau fichier

---

## 📅 JOUR 2 (25 Janvier - 1h) - ACTIONS RÉELLES

### Objectifs :
1. **Tester l'email SMTP**
   - Configurer `.env` avec vrais identifiants
   - Tester envoi réel
   - Documenter la procédure

2. **Ajouter formulaire de contact** (optionnel)
   - Parser le formulaire du site IMT
   - Fonction POST avec requests

### Fichiers à modifier :
- `app/tools.py` : Vérifier/améliorer `send_email`
- `.env` : Configuration personnelle (non versionnée)
- `README.md` : Documentation email

---

## 📅 JOUR 3 (26 Janvier - 1h) - LANGCHAIN

### Objectifs :
1. **Intégrer LangChain**
   - Ajouter `langchain` à requirements
   - Créer des Tool pour search et email
   - Utiliser AgentExecutor

2. **Refactorer l'agent**
   - Remplacer logique maison par LangChain
   - Garder la simplicité

### Fichiers à modifier :
- `requirements.txt` : Ajouter langchain
- `app/agent.py` : Intégration LangChain
- `app/tools.py` : Adapter pour LangChain Tools

---

## 📅 JOUR 4 (27 Janvier - 1h) - LANGFUSE

### Objectifs :
1. **Ajouter Langfuse**
   - Créer compte gratuit
   - Installer SDK
   - Configurer clés API

2. **Tracer les appels LLM**
   - Envelopper les appels Gemini
   - Monitorer coûts et latence

### Fichiers à modifier :
- `requirements.txt` : Ajouter langfuse
- `app/agent.py` : Intégration Langfuse
- `.env.example` : Variables Langfuse

---

## 📅 JOUR 5 (28 Janvier - 1h) - RAG AVANCÉ

### Objectifs :
1. **Améliorer la recherche sémantique**
   - Ajouter `sentence-transformers`
   - Générer embeddings des chunks
   - Utiliser similarité cosinus

2. **Créer script d'indexation**
   - Modifier `build_index.py`
   - Pré-calculer embeddings
   - Stocker dans JSON

### Fichiers à modifier :
- `requirements.txt` : Ajouter sentence-transformers
- `scripts/build_embeddings.py` : Nouveau fichier
- `app/tools.py` : Utiliser embeddings
- `scripts/build_index.py` : Enrichir

---

## 📅 JOUR 6 (29 Janvier - 1h) - INTERFACE + NETTOYAGE

### Objectifs :
1. **Améliorer Chainlit**
   - Boutons d'action
   - Messages d'erreur clairs
   - Commandes spéciales (/email, /update)

2. **Nettoyer le code**
   - Supprimer code commenté
   - Créer `config.py` centralisé
   - Améliorer documentation

### Fichiers à modifier :
- `chainlit_app.py` : Améliorations UI
- `config.py` : Nouveau fichier
- `README.md` : Documentation complète
- Tous les fichiers : Nettoyage

---

## 📅 JOUR 7 (30 Janvier - Matinée) - FINALISATION

### Objectifs :
1. **Tests complets**
   - Lancer tous les tests
   - Vérifier toutes les fonctionnalités
   - Corriger bugs restants

2. **Documentation finale**
   - README complet
   - Captures d'écran
   - Guide d'installation

3. **Archive pour remise**
   - Zip du projet
   - Vérification finale

---

## 🎯 PRIORITÉS

### Haute priorité (Obligatoire) :
- ✅ SDK Gemini fonctionnel
- ✅ Tests basiques
- ⏳ LangChain (Jour 3)
- ⏳ Langfuse (Jour 4)
- ⏳ RAG avancé (Jour 5)

### Moyenne priorité (Important) :
- ⏳ Email réel (Jour 2)
- ⏳ Interface améliorée (Jour 6)
- ⏳ Documentation (Jour 6-7)

### Basse priorité (Bonus) :
- Formulaire de contact automatique
- Commandes spéciales Chainlit
- Dashboard de monitoring

---

## 📊 MÉTRIQUES DE SUCCÈS

- [ ] Agent répond correctement aux questions sur l'IMT
- [ ] Email envoyé avec succès
- [ ] Tous les tests passent
- [ ] LangChain intégré
- [ ] Langfuse trace les appels
- [ ] RAG avec embeddings fonctionne
- [ ] Interface Chainlit claire
- [ ] Documentation complète
- [ ] Projet prêt pour remise

---

*Dernière mise à jour : 23 Janvier 2026, 17h00*
