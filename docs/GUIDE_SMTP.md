# 📧 Guide de Configuration SMTP - Envoi d'Emails Réels

Ce guide explique comment configurer l'envoi d'emails réels avec l'agent IMT.

---

## 🎯 Vue d'ensemble

L'agent IMT peut envoyer de vrais emails via SMTP. Par défaut, il fonctionne en **mode simulation** si aucune configuration n'est fournie.

### Modes de fonctionnement

| Mode | Configuration | Comportement |
|------|---------------|--------------|
| **Simulation** | Aucune | Affiche l'email sans l'envoyer |
| **Réel** | Variables d'environnement | Envoie vraiment l'email |

---

## 📝 Configuration Étape par Étape

### Méthode 1 : Gmail (Recommandé)

#### Étape 1 : Activer la validation en 2 étapes
1. Aller sur [myaccount.google.com](https://myaccount.google.com)
2. Menu **Sécurité** → **Validation en 2 étapes**
3. Suivre les instructions pour activer

#### Étape 2 : Créer un mot de passe d'application
1. Aller sur [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Sélectionner **App** : "Mail"
3. Sélectionner **Appareil** : "Autre (nom personnalisé)"
4. Saisir : "IMT Agent"
5. Cliquer sur **Générer**
6. **Copier le mot de passe de 16 caractères** (sans espaces)

⚠️ **Important** : Ce mot de passe ne s'affiche qu'une seule fois !

#### Étape 3 : Configurer le fichier `.env`
Créer/éditer le fichier `.env` à la racine du projet :

```bash
# Configuration Email SMTP
EMAIL_USER=votre_email@gmail.com
EMAIL_PASS=abcd efgh ijkl mnop    # Mot de passe d'application (16 caractères)
EMAIL_TO=directeur@imt.sn          # Destinataire par défaut

# Configuration serveur (optionnel, valeurs par défaut OK pour Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

**Exemple complet** :
```env
EMAIL_USER=john.doe@gmail.com
EMAIL_PASS=abcdefghijklmnop
EMAIL_TO=contact@imt.sn
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

---

### Méthode 2 : Outlook / Hotmail

#### Configuration Outlook.com
```env
EMAIL_USER=votre_email@outlook.com
EMAIL_PASS=votre_mot_de_passe
EMAIL_TO=destinataire@example.com
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
```

⚠️ **Note** : Outlook peut nécessiter l'activation de "Applications moins sécurisées"

---

### Méthode 3 : Autre Fournisseur

#### Serveurs SMTP courants

| Fournisseur | SMTP_HOST | SMTP_PORT |
|-------------|-----------|-----------|
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp-mail.outlook.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |
| SendGrid | smtp.sendgrid.net | 587 |
| Mailgun | smtp.mailgun.org | 587 |

---

## 🧪 Test de la Configuration

### Test en ligne de commande

```bash
# Activer l'environnement
source venv/bin/activate

# Tester l'envoi d'email
python -c "
from app.tools import send_email
result = send_email('Test IMT Agent', 'Ceci est un test')
print(result)
"
```

### Test avec l'agent complet

```bash
python -m app.agent
# Puis poser : "envoyer un email au directeur pour demander des informations"
```

### Test avec Chainlit

```bash
chainlit run chainlit_app.py
# Dans l'interface : "Je veux contacter le directeur"
```

---

## ✅ Vérification de la Configuration

### Checklist de vérification

- [ ] Fichier `.env` créé à la racine du projet
- [ ] `EMAIL_USER` défini avec une adresse valide
- [ ] `EMAIL_PASS` défini (mot de passe d'application pour Gmail)
- [ ] `EMAIL_TO` défini avec l'adresse du destinataire
- [ ] Variables chargées (test avec `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('EMAIL_USER'))"`)

### Messages de confirmation

**Mode simulation** :
```
📧 EMAIL NON ENVOYÉ (simulation)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Raison : Aucune configuration SMTP détectée.
```

**Envoi réussi** :
```
✅ EMAIL ENVOYÉ AVEC SUCCÈS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 Destinataire : directeur@imt.sn
📩 Sujet : Demande d'informations
✓ Serveur SMTP : smtp.gmail.com:587
```

---

## 🐛 Dépannage

### Erreur : "Authentification failed"

**Cause** : Identifiants incorrects

**Solutions** :
1. ✅ Vérifier que vous utilisez un **mot de passe d'application** (pas votre mot de passe Gmail normal)
2. ✅ Vérifier qu'il n'y a pas d'espaces dans le mot de passe
3. ✅ Vérifier que la validation en 2 étapes est activée
4. ✅ Régénérer un nouveau mot de passe d'application

**Test** :
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('User:', os.getenv('EMAIL_USER')); print('Pass length:', len(os.getenv('EMAIL_PASS', '')))"
```

---

### Erreur : "Connection refused"

**Cause** : Serveur ou port incorrect

**Solutions** :
1. ✅ Vérifier `SMTP_HOST=smtp.gmail.com` (pas mail.google.com)
2. ✅ Vérifier `SMTP_PORT=587` (pas 465 ou 25)
3. ✅ Tester votre connexion internet

**Test de connexion** :
```bash
telnet smtp.gmail.com 587
# Devrait afficher "Connected to smtp.gmail.com"
# Ctrl+] puis "quit" pour sortir
```

---

### Erreur : "Timeout"

**Cause** : Firewall ou connexion lente

**Solutions** :
1. ✅ Vérifier que votre firewall autorise le port 587
2. ✅ Essayer un autre réseau (désactiver VPN si actif)
3. ✅ Vérifier votre connexion internet

---

### Erreur : "Sender address rejected"

**Cause** : Adresse email invalide

**Solutions** :
1. ✅ Vérifier le format de `EMAIL_USER` (doit contenir @)
2. ✅ Vérifier qu'il n'y a pas d'espaces avant/après
3. ✅ Utiliser une adresse email existante

---

### L'email n'arrive pas

**Vérifications** :
1. ✅ Vérifier les **spams** du destinataire
2. ✅ Vérifier que `EMAIL_TO` est correct
3. ✅ Attendre 5-10 minutes (délais possibles)
4. ✅ Vérifier dans "Messages envoyés" de Gmail

---

## 🔒 Sécurité

### Bonnes pratiques

1. **Ne jamais versionner `.env`**
   - Le fichier `.env` est déjà dans `.gitignore`
   - Ne jamais commit vos identifiants

2. **Utiliser des mots de passe d'application**
   - Plus sécurisé que votre mot de passe principal
   - Peut être révoqué sans changer votre mot de passe principal

3. **Limiter les permissions**
   - Créer un compte email dédié pour l'agent
   - Ne pas utiliser votre email personnel principal

4. **Rotation des mots de passe**
   - Changer régulièrement les mots de passe d'application
   - Révoquer ceux qui ne sont plus utilisés

---

## 📊 Limites et Quotas

### Gmail
- **Limite** : 500 emails par jour
- **Burst** : ~100 emails par heure
- **Taille** : 25 MB par email (avec pièces jointes)

### Outlook
- **Limite** : 300 emails par jour
- **Destinataires** : 100 par email

**Conseil** : Pour un usage intensif, considérer un service SMTP dédié (SendGrid, Mailgun).

---

## 🧪 Tests Avancés

### Test avec pytest

```bash
pytest tests/test_tools.py::test_send_email_simulation -v
```

### Test de validation email

```python
from app.tools import _validate_email

print(_validate_email("test@example.com"))  # True
print(_validate_email("invalid"))           # False
```

---

## 📚 Ressources

- [Créer mot de passe d'application Gmail](https://support.google.com/accounts/answer/185833)
- [Configuration SMTP Gmail](https://support.google.com/mail/answer/7126229)
- [Documentation smtplib Python](https://docs.python.org/3/library/smtplib.html)

---

## 💡 FAQ

**Q : Puis-je utiliser Gmail sans validation en 2 étapes ?**  
R : Non, Google l'exige pour les mots de passe d'application depuis 2022.

**Q : Le mot de passe d'application fonctionne-t-il avec IMAP ?**  
R : Oui, il fonctionne pour tous les protocoles (SMTP, IMAP, POP3).

**Q : Puis-je envoyer à plusieurs destinataires ?**  
R : Actuellement non, mais cela peut être ajouté en modifiant `send_email()`.

**Q : L'agent stocke-t-il mes identifiants ?**  
R : Non, ils sont lus depuis `.env` à chaque utilisation et jamais sauvegardés.

---

*Dernière mise à jour : 23 Janvier 2026*
