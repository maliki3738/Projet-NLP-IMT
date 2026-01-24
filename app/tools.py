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

# Configuration du logging
logger = logging.getLogger(__name__)

def search_imt(query: str) -> str:
    """Recherche des informations dans la base de données IMT.
    
    Cette fonction analyse la question, identifie le fichier source pertinent,
    et extrait les informations réelles des données scrapées.
    
    Args:
        query: La question de recherche
        
    Returns:
        Réponse extraite des données ou message d'erreur
    """
    if not query or not query.strip():
        logger.warning("Recherche avec query vide")
        return "Veuillez poser une question valide."
    
    logger.debug(f"Recherche IMT pour: {query}")
    q_lower = query.lower()
    
    # Chargement des fichiers texte sources
    data_dir = Path("data")
    
    # Mapping mots-clés -> fichiers sources
    source_mapping = {
        "formations.txt": ["formation", "bachelor", "programme", "diplôme", "étude", "cursus", "enseigne", "apprendre"],
        "contact.txt": ["contact", "téléphone", "appeler", "joindre", "numéro", "adresse", "où", "ou", "localisation", "situé", "trouve"],
        "Edulab.txt": ["edulab", "laboratoire", "espace", "expérimentation"],
        "accueil.txt": ["événement", "actualité", "actu", "nouveau", "quoi de neuf", "news"]
    }
    
    # Identifier le(s) fichier(s) pertinent(s)
    relevant_sources = []
    for source_file, keywords in source_mapping.items():
        if any(keyword in q_lower for keyword in keywords):
            relevant_sources.append(source_file)
    
    # Si aucun fichier spécifique, chercher partout
    if not relevant_sources:
        relevant_sources = list(source_mapping.keys())
    
    logger.info(f"Fichiers pertinents identifiés: {relevant_sources}")
    
    # Lire et analyser les fichiers pertinents
    all_content = []
    for source_file in relevant_sources:
        file_path = data_dir / source_file
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8")
                all_content.append({
                    "source": source_file,
                    "content": content,
                    "lines": [l.strip() for l in content.split('\n') if l.strip() and len(l.strip()) > 20]
                })
                logger.debug(f"Chargé {source_file}: {len(content)} caractères")
            except Exception as e:
                logger.error(f"Erreur lecture {source_file}: {e}")
    
    if not all_content:
        logger.error("Aucune donnée chargée")
        return "Les données IMT ne sont pas disponibles. Veuillez réessayer plus tard."
    
    # === ANALYSE INTELLIGENTE DE LA QUESTION ===
    
    # Extraire les mots-clés importants (> 3 lettres, pas de mots vides)
    stop_words = {"est", "sont", "dans", "pour", "avec", "des", "les", "une", "qui", "quoi", "quel", "quelle", "comment"}
    query_words = [w for w in q_lower.split() if len(w) > 3 and w not in stop_words]
    
    logger.debug(f"Mots-clés extraits: {query_words}")
    
    # Chercher les lignes les plus pertinentes dans tous les fichiers
    scored_lines = []
    for doc in all_content:
        for line in doc["lines"]:
            line_lower = line.lower()
            # Calculer un score de pertinence
            score = sum(1 for word in query_words if word in line_lower)
            
            # Bonus si le fichier source est très pertinent
            if doc["source"] in relevant_sources[:1]:  # Premier fichier le plus pertinent
                score += 0.5
            
            if score > 0:
                scored_lines.append({
                    "line": line,
                    "score": score,
                    "source": doc["source"]
                })
    
    # Trier par score décroissant
    scored_lines.sort(key=lambda x: x["score"], reverse=True)
    
    if not scored_lines:
        logger.info("Aucune ligne pertinente trouvée")
        return "Je n'ai pas trouvé d'information pertinente sur cette question dans nos données. Pouvez-vous reformuler ou être plus précis ?"
    
    # Prendre les 3 meilleures lignes
    best_lines = scored_lines[:3]
    
    logger.info(f"Trouvé {len(best_lines)} lignes pertinentes (score max: {best_lines[0]['score']})")
    
    # Construire la réponse à partir des lignes trouvées
    response_parts = []
    seen_content = set()  # Pour éviter les doublons
    
    for item in best_lines:
        line = item["line"].strip()
        
        # Nettoyer les balises [EVENEMENT], [FORMATION], etc.
        if line.startswith('[') and ']' in line:
            line = line.split(']', 1)[1].strip()
        
        # Éviter les doublons et lignes trop courtes
        if line not in seen_content and len(line) > 30:
            response_parts.append(line)
            seen_content.add(line)
    
    if not response_parts:
        # Fallback: retourner le début du contenu le plus pertinent
        best_doc = all_content[0]
        first_line = best_doc["lines"][0] if best_doc["lines"] else "Aucune information trouvée."
        # Nettoyer aussi le fallback
        if first_line.startswith('[') and ']' in first_line:
            first_line = first_line.split(']', 1)[1].strip()
        return first_line
    
    # Joindre les parties de réponse
    response = " ".join(response_parts[:2])  # Limiter à 2 lignes pour éviter trop de texte
    
    logger.info(f"Réponse construite: {response[:100]}...")
    return response

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