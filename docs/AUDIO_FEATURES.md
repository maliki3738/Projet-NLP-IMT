# 🎤🔊 Fonctionnalités Audio - Agent IMT Dakar

## ✅ Problème résolu

**Avant** : Popup d'autorisation microphone à chaque clic (causé par `imt-bg.js` ligne 299)
**Maintenant** : Animation visuelle sans micro + fonctionnalités audio natives Chainlit

## 🎯 Fonctionnalités activées

### 1️⃣ **Speech-to-Text (STT)** 🎤
**Usage** :
- Cliquez sur l'icône **microphone** dans la barre de saisie
- Parlez (max 15 secondes)
- Votre parole est transcrite automatiquement en texte
- Appuyez sur Entrée pour envoyer

**Configuration** :
```toml
[features.audio]
enabled = true
min_decibels = -45              # Sensibilité micro
initial_silence_timeout = 3000   # 3s avant annulation si silence
silence_timeout = 1500           # 1.5s pause = fin d'enregistrement
max_duration = 15000             # 15s max par enregistrement
sample_rate = 44100              # Qualité CD
chunk_duration = 1000            # Traitement par tranches de 1s
```

### 2️⃣ **Text-to-Speech (TTS)** 🔊
**Usage** :
- Survolez un message de l'agent
- Cliquez sur l'icône **haut-parleur** qui apparaît
- Le texte est lu à voix haute
- Cliquez à nouveau pour arrêter

**Navigateurs supportés** :
- ✅ Chrome/Edge : Web Speech API native
- ✅ Firefox : Web Speech API native
- ✅ Safari : Web Speech API (voix iOS/macOS)

## 🔧 Configuration technique

### Paramètres STT optimisés
| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| `min_decibels` | -45 | Seuil de détection (plus bas = plus sensible) |
| `initial_silence_timeout` | 3000ms | Temps avant annulation si aucun son |
| `silence_timeout` | 1500ms | Durée de silence = fin d'enregistrement |
| `max_duration` | 15000ms | Durée max par message vocal |
| `sample_rate` | 44100Hz | Qualité audio (standard CD) |

### API utilisée par Chainlit
**Speech Recognition API** (native navigateur) :
```javascript
const recognition = new webkitSpeechRecognition() || new SpeechRecognition();
recognition.lang = 'fr-FR';  // Défini dans config.toml UI.language
recognition.continuous = false;
recognition.interimResults = true;
```

**Speech Synthesis API** (TTS) :
```javascript
const utterance = new SpeechSynthesisUtterance(text);
utterance.lang = 'fr-FR';
speechSynthesis.speak(utterance);
```

## 🎨 Interface utilisateur

### Barre de saisie
```
┌────────────────────────────────────────────┐
│ [🎤] Tapez votre message ici...      [📎] │
└────────────────────────────────────────────┘
     ↑
  Bouton STT (parler au lieu de taper)
```

### Message de l'agent
```
┌────────────────────────────────────────────┐
│ Agent IMT Dakar               [🔊] [📋]    │
│                                ↑           │
│ L'Institut Mines-Télécom...  TTS (écouter)│
└────────────────────────────────────────────┘
```

## 🎤 Démonstration pour la soutenance

### Scénario 1 : STT (dicter un message)
1. Ouvrir l'interface : http://localhost:8000
2. Cliquer sur l'icône 🎤 dans la barre de saisie
3. Dire : *"Quelles sont les formations disponibles ?"*
4. Le texte apparaît automatiquement
5. Appuyer sur Entrée

**Résultat** : Message envoyé sans taper au clavier

### Scénario 2 : TTS (écouter la réponse)
1. L'agent répond avec du texte long
2. Survoler le message
3. Cliquer sur l'icône 🔊
4. La voix synthétique lit le texte en français

**Résultat** : Accessibilité pour personnes malvoyantes ou en situation de mobilité

## ⚠️ Limitations connues

### STT (Reconnaissance vocale)
- ❌ Nécessite connexion Internet (API Google/Apple)
- ❌ Qualité dépend du micro et du bruit ambiant
- ❌ Limite 15s par enregistrement (configurable)
- ❌ Peut avoir du mal avec accents forts ou jargon technique

### TTS (Synthèse vocale)
- ❌ Voix robotique (pas naturelle comme Gemini Audio)
- ❌ Qualité variable selon navigateur (meilleure sur Chrome)
- ❌ Pas de contrôle de vitesse/tonalité via UI Chainlit

## 🚀 Améliorations futures

### Court terme
- [ ] Ajouter shortcut clavier (Ctrl+M) pour activer STT
- [ ] Feedback visuel pendant enregistrement (onde audio)
- [ ] Notification si micro non disponible/bloqué

### Long terme
- [ ] Intégrer Gemini Audio API pour TTS naturelle
- [ ] Transcription STT locale (Whisper.cpp) sans Internet
- [ ] Support multi-langues (arabe, anglais, wolof)

## 🐛 Dépannage

### "Microphone non détecté"
1. Vérifier permissions navigateur : `chrome://settings/content/microphone`
2. Tester micro : Paramètres > Son > Entrée
3. Relancer Chainlit

### "Pas d'autorisation micro"
- Si Chrome/Edge : Cliquer sur 🔒 dans barre URL > Autoriser Microphone
- Si Firefox : Cliquer sur 🎤 dans barre URL > Autoriser
- Si Safari : Préférences > Sites web > Microphone > Autoriser

### TTS ne lit pas le texte
1. Vérifier volume système (pas muet)
2. Tester : Console navigateur > `speechSynthesis.speak(new SpeechSynthesisUtterance("test"))`
3. Essayer autre navigateur (Chrome recommandé)

## 📊 Métadonnées techniques

**Fichiers modifiés** :
- `.chainlit/config.toml` : `[features.audio] enabled = true`
- `public/imt-bg.js` : Supprimé `getUserMedia` (ligne 299-307)

**APIs natives** :
- Web Speech API (STT) : https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- Speech Synthesis API (TTS) : https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis

**Compatibilité** :
- Chrome/Edge ≥ 33 ✅
- Firefox ≥ 49 ✅
- Safari ≥ 14.1 ✅
- Mobile iOS/Android ✅ (permissions requises)

## 🎓 Pour la soutenance

**Message clé** :
> "Nous avons intégré les fonctionnalités Speech-to-Text et Text-to-Speech natives du navigateur via Chainlit, permettant une interaction mains-libres et améliorant l'accessibilité pour les utilisateurs en situation de handicap visuel ou moteur."

**Démo 30 secondes** :
1. Montrer bouton micro 🎤
2. Dicter "Parle-moi de l'Edulab"
3. Recevoir réponse textuelle
4. Cliquer sur 🔊 pour écouter
5. Expliquer : "Aucune popup d'autorisation intrusive, tout est géré proprement"

**Point fort** : Accessibilité et UX moderne sans dépendance externe (API gratuite navigateur)
