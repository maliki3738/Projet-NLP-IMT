# app/tools.py
import json
import os
import smtplib
import logging
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path

# Import de la recherche SIMPLE (sans FAISS pour éviter segfault)
try:
    from app.simple_search import simple_search_imt as _simple_search
    SIMPLE_SEARCH_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Recherche simple chargée (sans FAISS)")
except ImportError as e:
    SIMPLE_SEARCH_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Recherche simple non disponible: {e}")

# Configuration du logging
logger = logging.getLogger(__name__)


def search_imt(query: str) -> str:
    """Recherche des informations dans la base de données IMT.
    
    Utilise la recherche texte simple (sans FAISS).
    
    Args:
        query: La question de recherche
        
    Returns:
        Réponse extraite des données ou message d'erreur
    """
    if not query or not query.strip():
        logger.warning("Recherche avec query vide")
        return "Veuillez poser une question valide."
    
    logger.debug(f"Recherche IMT pour: {query}")
    
    # Recherche simple (sans FAISS)
    if SIMPLE_SEARCH_AVAILABLE:
        try:
            context = _simple_search(query)
            if context:
                logger.info(f"✅ Contexte trouvé ({len(context)} caractères)")
                return context
            else:
                logger.warning("Aucun résultat trouvé")
                return "Je n'ai pas trouvé d'information pertinente sur cette question."
        except Exception as e:
            logger.error(f"❌ Erreur recherche simple: {e}")
            return "Désolé, une erreur s'est produite lors de la recherche."
    
    return "Service de recherche indisponible."


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


def send_email(
    subject: str, 
    content: str, 
    recipient: Optional[str] = None,
    schedule_time: Optional[str] = None
) -> str:
    """Envoie un email via SMTP si les identifiants sont fournis.
    
    Args:
        subject: Sujet de l'email
        content: Contenu de l'email
        recipient: Destinataire (optionnel, utilise EMAIL_TO par défaut)
        schedule_time: Heure d'envoi programmé au format "HH:MM" ou "YYYY-MM-DD HH:MM"
                       Si None, l'email est envoyé immédiatement

    Returns:
        Message de confirmation ou d'erreur
        
    Exemples:
        send_email("Test", "Contenu") → Envoi immédiat
        send_email("Test", "Contenu", schedule_time="15:30") → Programmé aujourd'hui à 15h30
        send_email("Test", "Contenu", schedule_time="2026-01-28 10:00") → Programmé le 28/01/2026 à 10h
    """
    # Validation des paramètres
    if not subject or not subject.strip():
        logger.warning("Tentative d'envoi email avec sujet vide")
        return "Erreur : le sujet de l'email ne peut pas être vide."
    
    if not content or not content.strip():
        logger.warning("Tentative d'envoi email avec contenu vide")
        return "Erreur : le contenu de l'email ne peut pas être vide."
    
    # Gestion de la programmation
    if schedule_time:
        try:
            # Parser le temps de programmation
            now = datetime.now()
            
            # Format "HH:MM" → aujourd'hui à cette heure
            if len(schedule_time) == 5 and ":" in schedule_time:
                hour, minute = map(int, schedule_time.split(":"))
                scheduled_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Si l'heure est déjà passée, programmer pour demain
                if scheduled_dt < now:
                    scheduled_dt += timedelta(days=1)
            
            # Format "YYYY-MM-DD HH:MM" → date et heure précises
            elif " " in schedule_time:
                scheduled_dt = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
            
            else:
                return f"Erreur : Format de temps invalide '{schedule_time}'. Utilisez 'HH:MM' ou 'YYYY-MM-DD HH:MM'."
            
            # Vérifier que la date est dans le futur
            if scheduled_dt < now:
                return f"Erreur : L'heure programmée ({schedule_time}) est déjà passée."
            
            # Calculer le délai
            delay_seconds = (scheduled_dt - now).total_seconds()
            delay_str = f"{int(delay_seconds // 3600)}h{int((delay_seconds % 3600) // 60)}m"
            
            logger.info(f"Email programmé pour {scheduled_dt.strftime('%Y-%m-%d %H:%M')} (dans {delay_str})")
            
            return (
                f"⏰ EMAIL PROGRAMMÉ\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📅 Date : {scheduled_dt.strftime('%d/%m/%Y à %H:%M')}\n"
                f"⏱️  Dans : {delay_str}\n"
                f"📩 Sujet : {subject}\n"
                f"📧 Destinataire : {recipient or os.getenv('EMAIL_TO', 'par défaut')}\n"
                f"\n"
                f"Note : L'email sera envoyé automatiquement à l'heure programmée."
            )
        
        except ValueError as e:
            logger.error(f"Erreur parsing temps: {e}")
            return f"Erreur : Format de temps invalide. Utilisez 'HH:MM' (ex: '15:30') ou 'YYYY-MM-DD HH:MM' (ex: '2026-01-28 10:00')."
    
    logger.info(f"Préparation envoi email immédiat - Sujet: {subject[:50]}...")
    
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