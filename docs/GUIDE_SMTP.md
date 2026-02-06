# 📧 Configuration SMTP - Envoi d'Emails

> Guide rapide pour configurer l'envoi d'emails réels avec Gmail ou Outlook.

---

## Configuration Gmail (Recommandé)

### 1. Créer un Mot de Passe d'Application

1. Activer la **Validation en 2 étapes** : [myaccount.google.com](https://myaccount.google.com) → Sécurité
2. Créer un **Mot de passe d'application** : [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - App : Mail
   - Appareil : Autre (IMT Agent)
   - Copier le code 16 caractères généré

### 2. Configuration `.env`

```env
# Email SMTP
EMAIL_USER=votre_email@gmail.com
EMAIL_PASS=abcdefghijklmnop  # Mot de passe application (16 car.)
EMAIL_TO=contact@imt.sn

# Serveur (optionnel, valeurs par défaut)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

---

## Configuration Outlook

```env
EMAIL_USER=votre_email@outlook.com
EMAIL_PASS=votre_mot_de_passe
EMAIL_TO=destinataire@example.com
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
```

---

## Serveurs SMTP Courants

| Fournisseur | SMTP_HOST | Port |
|-------------|-----------|------|
| Gmail | smtp.gmail.com | 587 |
| Outlook | smtp-mail.outlook.com | 587 |
| Yahoo | smtp.mail.yahoo.com | 587 |

---

## Test

```bash
# Test rapide
python -c "from app.tools import send_email; print(send_email('Test', 'Ceci est un test'))"

# Doit afficher
✅ Email envoyé avec succès !
```

---

## Dépannage

| Erreur | Solution |
|--------|----------|
| `Authentication failed` | Vérifier EMAIL_USER et EMAIL_PASS |
| `Connection refused` | Vérifier SMTP_HOST et SMTP_PORT |
| `Recipient refused` | Vérifier EMAIL_TO (email valide) |

**Logs** : Vérifier dans la console Chainlit ou avec `pytest tests/test_tools.py -v`

---

**Documentation** : [app/tools.py](../app/tools.py) (fonction `send_email`)

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
