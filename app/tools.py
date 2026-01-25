# app/tools.py
import json
import os
import smtplib
import logging
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from difflib import get_close_matches
from pathlib import Path

# Import du nouveau moteur de recherche vectorielle
try:
    from app.vector_search import vector_search_imt as _vector_search
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Recherche vectorielle non disponible, utilisation du fallback manuel")

# Configuration du logging
logger = logging.getLogger(__name__)

def extract_best_paragraph(text: str, query_words: list[str], is_primary_source: bool = False) -> tuple[str, float]:
    """Extrait le meilleur paragraphe d'un texte basé sur les mots-clés.
    
    Args:
        text: Le texte complet
        query_words: Liste de mots-clés de la question
        is_primary_source: True si ce fichier est le premier match du routing
        
    Returns:
        Tuple (paragraphe, score) ou ("", -999) si rien trouvé
    """
    # Essayer d'abord de découper par double saut de ligne
    paragraphs = re.split(r"\n\s*\n", text)
    
    # Si un seul gros paragraphe, découper par ligne simple
    if len(paragraphs) == 1:
        paragraphs = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 40]
    
    logger.debug(f"🔍 Analyse: {len(paragraphs)} paragraphes, mots-clés: {query_words}, primaire: {is_primary_source}")
    
    scored = []

    for idx, p in enumerate(paragraphs):
        p_lower = p.lower()
        score = sum(1 for w in query_words if w in p_lower)
        
        # Bonus FORT pour correspondance exacte mots-clés importants
        if any(word in p_lower for word in ["téléphone", "email", "adresse", "km1", "avenue"]):
            score += 2
        
        # Bonus FORT pour phrases descriptives officielles (plus robuste)
        if "institut mines" in p_lower or "mines télécom" in p_lower or "mines-télécom" in p_lower:
            score += 3
        
        # Bonus léger pour les premières lignes
        if idx < 5:
            score += 0.3
        
        # Bonus FORT pour fichier primaire (premier match du routing)
        if is_primary_source:
            score += 5
        
        # Malus léger UNIQUEMENT si vraiment trop court
        if len(p) < 60:
            score -= 0.5
        
        # Malus pour les témoignages
        if "»" in p or "«" in p or "mon parcours" in p_lower:
            score -= 3
        
        if score > -2:  # Permettre scores légèrement négatifs
            scored.append((score, p.strip()))
            if score > 0 and idx < 10:  # Log des 10 premiers avec score positif
                logger.debug(f"  [{idx}] Score {score:.1f}: {p[:80]}...")

    scored.sort(reverse=True, key=lambda x: x[0])
    
    if scored:
        best_score, best_text = scored[0][0], scored[0][1]
        
        # Si le meilleur résultat est trop long (> 500 chars), prendre seulement les 2-3 premières phrases
        if len(best_text) > 500:
            # Prendre les 3 premières lignes du texte
            lines = best_text.split('\n')
            best_text = '\n'.join(lines[:3]) if len(lines) > 3 else best_text[:500]
            logger.debug(f"✂️ Texte tronqué à {len(best_text)} chars")
        
        logger.debug(f"✅ Meilleur: score={best_score:.1f}, texte={best_text[:100]}...")
        return (best_text, best_score)
    else:
        logger.debug(f"❌ Aucun paragraphe avec score > -2")
        return ("", -999)

def search_imt(query: str) -> str:
    """Recherche des informations dans la base de données IMT.
    
    Cette fonction utilise la recherche vectorielle sémantique (RAG) si disponible,
    sinon fallback vers le scoring manuel basique.
    
    Args:
        query: La question de recherche
        
    Returns:
        Réponse extraite des données ou message d'erreur
    """
    if not query or not query.strip():
        logger.warning("Recherche avec query vide")
        return "Veuillez poser une question valide."
    
    logger.debug(f"Recherche IMT pour: {query}")
    
    # OPTION 1 : Recherche vectorielle (RAG) - Prioritaire
    if VECTOR_SEARCH_AVAILABLE:
        try:
            results = _vector_search(query, top_k=1)
            if results and results[0]['score'] > 0.3:  # Seuil de confiance
                best = results[0]
                logger.info(f"✅ Réponse RAG trouvée: {best['source']} (score: {best['score']:.3f})")
                return best['content']
        except Exception as e:
            logger.error(f"❌ Erreur recherche vectorielle: {e}, fallback vers scoring manuel")
    
    # OPTION 2 : Fallback scoring manuel (ancien système)
    logger.info("📊 Utilisation du scoring manuel (fallback)")
    return _search_imt_manual(query)


def _search_imt_manual(query: str) -> str:
    """Ancien système de recherche par scoring manuel (fallback).
    
    Conservé pour compatibilité si la recherche vectorielle échoue.
    """
    q_lower = query.lower()
    
    # Chargement des fichiers texte sources
    data_dir = Path("data")
    
    # Mapping mots-clés -> fichiers sources (amélioré)
    source_mapping = {
        "formations.txt": ["formation", "bachelor", "programme", "diplôme", "étude", "cursus", "enseigne", "apprendre", "master", "cours"],
        "contact.txt": ["contact", "téléphone", "appeler", "joindre", "numéro", "adresse", "où", "ou", "localisation", "situé", "trouve", "mail"],
        "Edulab.txt": ["edulab", "laboratoire", "espace", "expérimentation", "lab", "projet", "fablab"],
        "accueil.txt": ["événement", "actualité", "actu", "nouveau", "quoi de neuf", "news"],
        "qui_sommes_nous.txt": ["qui", "sommes", "présentation", "imt", "institut", "c'est quoi", "qu'est-ce", "à propos"]
    }
    
    # CORRECTION 1 : Forcer qui_sommes_nous si question identitaire
    if any(x in q_lower for x in ["c'est quoi", "qu'est-ce", "présentation", "définition"]) and ("imt" in q_lower or "institut" in q_lower):
        relevant_sources = ["qui_sommes_nous.txt"]
        logger.info("🎯 Question identitaire → qui_sommes_nous.txt")
    else:
        # Identifier le(s) fichier(s) pertinent(s)
        relevant_sources = []
        for source_file, keywords in source_mapping.items():
            if any(keyword in q_lower for keyword in keywords):
                relevant_sources.append(source_file)
        
        # Si aucun fichier spécifique, chercher partout
        if not relevant_sources:
            relevant_sources = list(source_mapping.keys())
        
        logger.info(f"Fichiers pertinents identifiés: {relevant_sources}")
    
    # CORRECTION 2 : Extraire les mots-clés de la question
    stop_words = {"est", "sont", "dans", "pour", "avec", "des", "les", "une", "qui", "quoi", "quel", "quelle", "comment", "c'est", "que", "qu"}
    
    # Nettoyer et normaliser les mots (enlever apostrophes, accents, etc.)
    clean_query = q_lower.replace("l'", " ").replace("d'", " ").replace("'", " ")
    query_words = [w for w in clean_query.split() if len(w) > 2 and w not in stop_words]
    
    # Si aucun mot-clé, utiliser mots génériques selon le contexte
    if not query_words:
        if "imt" in q_lower or "institut" in q_lower:
            query_words = ["institut", "mines", "télécom"]
        else:
            query_words = [clean_query.strip()]
    
    logger.debug(f"Mots-clés extraits: {query_words}")
    
    # CORRECTION 3 : Comparer les scores de TOUS les fichiers
    best_result = ("", -999)
    best_source = ""
    
    for idx, source_file in enumerate(relevant_sources):
        file_path = data_dir / source_file
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8")
                is_primary = (idx == 0)  # Premier fichier = plus pertinent
                paragraph, score = extract_best_paragraph(content, query_words, is_primary)
                if score > best_result[1]:
                    best_result = (paragraph, score)
                    best_source = source_file
                    logger.debug(f"Nouveau meilleur: {source_file} (score: {score})")
            except Exception as e:
                logger.error(f"Erreur lecture {source_file}: {e}")
    
    # Retourner le meilleur résultat trouvé
    if best_result[0]:
        logger.info(f"✅ Meilleure réponse trouvée dans {best_source} (score: {best_result[1]:.2f})")
        return best_result[0]
    
    # Si rien trouvé
    logger.warning("Aucune information pertinente trouvée")
    return "Information non trouvée dans les données IMT."


def _validate_email(email: str) -> bool:
    """Valide le format d'une adresse email.
    
    Args:
        email: L'adresse email à valider
        
    Returns:
        True si l'email est valide, False sinon
    """
    if not email:
        return False
    # Pattern simple de validation email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def send_email(subject: str, content: str, recipient: Optional[str] = None) -> str:
    """Envoie un email via SMTP si les identifiants sont fournis.
    
    Args:
        subject: Sujet de l'email
        content: Contenu de l'email
        recipient: Destinataire (optionnel, utilise EMAIL_TO par défaut)

    Returns:
        Message de confirmation ou d'erreur
    """
    # Validation des paramètres
    if not subject or not subject.strip():
        logger.warning("Tentative d'envoi email avec sujet vide")
        return "Erreur : le sujet de l'email ne peut pas être vide."
    
    if not content or not content.strip():
        logger.warning("Tentative d'envoi email avec contenu vide")
        return "Erreur : le contenu de l'email ne peut pas être vide."
    
    logger.info(f"Préparation envoi email - Sujet: {subject[:50]}...")
    
    # Récupération des variables d'environnement
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port_str = os.getenv("SMTP_PORT", "587")
    
    # Validation du port
    try:
        smtp_port = int(smtp_port_str)
        if smtp_port not in [25, 465, 587, 2525]:
            logger.warning(f"Port SMTP inhabituel: {smtp_port}")
    except ValueError:
        logger.error(f"Port SMTP invalide: {smtp_port_str}")
        smtp_port = 587
    
    # Mode simulation si pas de configuration
    if not email_user or not email_pass:
        logger.info("Mode simulation - pas de configuration SMTP")
        return (
            "📧 EMAIL NON ENVOYÉ (simulation)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Raison : Aucune configuration SMTP détectée.\n"
            "\n"
            "Pour envoyer de vrais emails, configurez dans .env :\n"
            "  EMAIL_USER=votre_email@gmail.com\n"
            "  EMAIL_PASS=votre_mot_de_passe_application\n"
            "  EMAIL_TO=destinataire@example.com\n"
            "\n"
            f"📩 Sujet : {subject}\n"
            f"📝 Contenu : {content[:100]}{'...' if len(content) > 100 else ''}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    
    # Validation de l'email utilisateur
    if not _validate_email(email_user):
        logger.error(f"Email utilisateur invalide: {email_user}")
        return f"Erreur : L'adresse email utilisateur '{email_user}' n'est pas valide."
    
    # Déterminer le destinataire
    email_to = recipient or os.getenv("EMAIL_TO") or email_user
    
    if not _validate_email(email_to):
        logger.error(f"Email destinataire invalide: {email_to}")
        return f"Erreur : L'adresse email destinataire '{email_to}' n'est pas valide."
    
    logger.info(f"Configuration SMTP - Host: {smtp_host}:{smtp_port}, De: {email_user}, Vers: {email_to}")
    
    # Création du message avec MIME
    try:
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_to
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain', 'utf-8'))
        
        logger.debug("Message MIME créé avec succès")
    except Exception as e:
        logger.error(f"Erreur création message MIME: {e}")
        return f"Erreur lors de la création du message : {e}"
    
    # Envoi de l'email
    try:
        logger.debug(f"Connexion à {smtp_host}:{smtp_port}...")
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
        server.ehlo()
        logger.debug("EHLO envoyé")
        
        if smtp_port == 587:
            logger.debug("Activation STARTTLS")
            server.starttls()
            server.ehlo()
        
        logger.debug("Tentative de connexion...")
        server.login(email_user, email_pass)
        logger.info("Connexion SMTP réussie")
        
        logger.debug("Envoi du message...")
        server.sendmail(email_user, email_to, msg.as_string())
        logger.info(f"Email envoyé avec succès vers {email_to}")
        
        server.quit()
        logger.debug("Connexion SMTP fermée")
        
        return (
            f"✅ EMAIL ENVOYÉ AVEC SUCCÈS\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📧 Destinataire : {email_to}\n"
            f"📩 Sujet : {subject}\n"
            f"✓ Serveur SMTP : {smtp_host}:{smtp_port}"
        )
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Erreur d'authentification SMTP: {e}")
        return (
            f"❌ ERREUR D'AUTHENTIFICATION\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Impossible de se connecter au serveur SMTP.\n"
            f"\n"
            f"Vérifiez que :\n"
            f"1. Votre email et mot de passe sont corrects\n"
            f"2. Vous utilisez un 'mot de passe d'application' (Gmail)\n"
            f"3. L'accès SMTP est activé sur votre compte\n"
            f"\n"
            f"Détails : {str(e)}"
        )
        
    except smtplib.SMTPConnectError as e:
        logger.error(f"Erreur de connexion SMTP: {e}")
        return (
            f"❌ ERREUR DE CONNEXION\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Impossible de se connecter au serveur {smtp_host}:{smtp_port}\n"
            f"\n"
            f"Vérifiez votre connexion internet et les paramètres du serveur.\n"
            f"Détails : {str(e)}"
        )
        
    except smtplib.SMTPException as e:
        logger.error(f"Erreur SMTP: {e}")
        return f"❌ Erreur SMTP : {str(e)}"
        
    except ConnectionRefusedError:
        logger.error(f"Connexion refusée par {smtp_host}:{smtp_port}")
        return (
            f"❌ CONNEXION REFUSÉE\n"
            f"Le serveur {smtp_host}:{smtp_port} refuse la connexion.\n"
            f"Vérifiez le host et le port dans votre configuration."
        )
        
    except TimeoutError:
        logger.error(f"Timeout connexion SMTP vers {smtp_host}:{smtp_port}")
        return (
            f"❌ TIMEOUT\n"
            f"La connexion au serveur {smtp_host}:{smtp_port} a expiré.\n"
            f"Vérifiez votre connexion internet ou essayez plus tard."
        )
        
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'envoi email: {e}", exc_info=True)
        return f"❌ Erreur inattendue : {str(e)}"