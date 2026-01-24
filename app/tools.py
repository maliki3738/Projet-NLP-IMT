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

# Configuration du logging
logger = logging.getLogger(__name__)

def search_imt(query: str) -> str:
    """Recherche des informations dans la base de données IMT.
    
    Args:
        query: La question de recherche
        
    Returns:
        Réponse trouvée ou message d'erreur approprié
    """
    if not query or not query.strip():
        logger.warning("Recherche avec query vide")
        return "Veuillez poser une question valide."
    
    logger.debug(f"Recherche IMT pour: {query}")
    q_lower = query.lower()
    
    # Chargement des données
    try:
        with open("data/chunks.json", "r", encoding="utf-8") as f:
            chunks = json.load(f)
        logger.debug(f"Chunks chargés: {len(chunks)} éléments")
    except FileNotFoundError:
        logger.error("Fichier chunks.json non trouvé")
        return "Les données IMT ne sont pas encore indexées. Veuillez exécuter 'python scripts/build_index.py'."
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de parsing JSON: {e}")
        return "Erreur de lecture des données IMT."
    except Exception as e:
        logger.error(f"Erreur inattendue lors du chargement: {e}")
        return "Une erreur s'est produite lors de la recherche."
    
    # Exception pour les questions de localisation
    location_keywords = ["où", "ou", "adresse", "localisation", "lieu", "emplacement", "situé", "trouve"]
    if any(word in q_lower for word in location_keywords):
        logger.debug("Détection question de localisation")
        for chunk in chunks:
            if chunk.get("source") == "contact.txt":
                lines = chunk.get("content", "").split('\n')
                for line in lines:
                    if "avenue" in line.lower() or "dakar" in line.lower():
                        logger.info(f"Adresse trouvée: {line.strip()[:50]}...")
                        return line.strip()
        logger.warning("Adresse non trouvée dans contact.txt")
        return "Adresse non trouvée. Contactez l'IMT pour plus d'informations."

    query_words = set(q_lower.split())
    logger.debug(f"Mots de recherche: {query_words}")
    
    # Trouver le chunk avec le plus de matches
    best_chunk = None
    max_matches = 0
    for chunk in chunks:
        content_lower = chunk.get("content", "").lower()
        match_count = sum(1 for word in query_words if word in content_lower)
        if match_count > max_matches:
            max_matches = match_count
            best_chunk = chunk
    
    if not best_chunk or max_matches == 0:
        logger.info(f"Aucune correspondance pour: {query}")
        return "Aucune information trouvée sur cette question. Essayez de reformuler ou contactez l'IMT directement."
    
    logger.debug(f"Meilleur chunk trouvé avec {max_matches} matches")
    
    # Extraire la ligne la plus pertinente
    lines = best_chunk.get("content", "").split('\n')
    relevant_lines = [
        line.strip() for line in lines 
        if len(line.strip()) > 10 and any(word in line.lower() for word in query_words)
    ]
    
    if relevant_lines:
        line = relevant_lines[0]
        # Nettoyer les préfixes comme [EVENEMENT]
        if line.startswith('[') and ']' in line:
            line = line.split(']', 1)[1].strip()
        logger.info(f"Réponse trouvée: {line[:50]}...")
        return line
    else:
        # Retourner le début du chunk si aucune ligne spécifique trouvée
        content = best_chunk.get("content", "")[:200]
        logger.debug("Retour du début du chunk")
        return content if content else "Aucune information pertinente trouvée."

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