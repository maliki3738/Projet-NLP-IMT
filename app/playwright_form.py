"""
Automatisation du formulaire de contact IMT avec Playwright.
Remplit et soumet le formulaire sur https://www.imt.sn/contact/
"""
import logging
import os
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)

CONTACT_URL = "https://www.imt.sn/contact/"

def fill_contact_form(
    name: str,
    email: str,
    subject: str,
    message: str,
    phone: Optional[str] = None
) -> str:
    """
    Remplit et soumet automatiquement le formulaire de contact IMT.
    
    Args:
        name: Nom complet de l'utilisateur
        email: Email de contact
        subject: Objet du message
        message: Contenu du message
        phone: Numéro de téléphone (optionnel)
        
    Returns:
        Message de succès ou d'erreur
    """
    try:
        logger.info(f"🌐 Ouverture du formulaire de contact : {CONTACT_URL}")
        
        with sync_playwright() as p:
            # Lancer le navigateur en mode headless
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            
            # Naviguer vers la page de contact
            page.goto(CONTACT_URL, wait_until="domcontentloaded", timeout=30000)
            logger.info("Page chargée")
            
            # Attendre que le formulaire soit visible
            page.wait_for_selector("form, input[type='text'], input[type='email']", timeout=10000)
            
            # Remplir les champs (sélecteurs adaptables selon la structure réelle)
            # Essayer plusieurs patterns de sélecteurs
            
            # Champ Nom
            name_selectors = [
                "input[name='your-name']",
                "input[name='name']",
                "input[placeholder*='Nom']",
                "input[placeholder*='nom']",
                "#nom", "#name"
            ]
            for selector in name_selectors:
                if page.query_selector(selector):
                    page.fill(selector, name)
                    logger.info(f"Nom rempli: {name}")
                    break
            
            # Champ Email
            email_selectors = [
                "input[name='your-email']",
                "input[name='email']",
                "input[type='email']",
                "#email"
            ]
            for selector in email_selectors:
                if page.query_selector(selector):
                    page.fill(selector, email)
                    logger.info(f"Email rempli: {email}")
                    break
            
            # Champ Téléphone (optionnel)
            if phone:
                phone_selectors = [
                    "input[name='your-phone']",
                    "input[name='phone']",
                    "input[name='tel']",
                    "input[type='tel']",
                    "#phone", "#tel"
                ]
                for selector in phone_selectors:
                    if page.query_selector(selector):
                        page.fill(selector, phone)
                        logger.info(f"Téléphone rempli: {phone}")
                        break
            
            # Champ Sujet
            subject_selectors = [
                "input[name='your-subject']",
                "input[name='subject']",
                "input[placeholder*='Sujet']",
                "input[placeholder*='sujet']",
                "#subject"
            ]
            for selector in subject_selectors:
                if page.query_selector(selector):
                    page.fill(selector, subject)
                    logger.info(f"Sujet rempli: {subject}")
                    break
            
            # Champ Message
            message_selectors = [
                "textarea[name='your-message']",
                "textarea[name='message']",
                "textarea[placeholder*='Message']",
                "textarea[placeholder*='message']",
                "#message"
            ]
            for selector in message_selectors:
                if page.query_selector(selector):
                    page.fill(selector, message)
                    logger.info(f"Message rempli ({len(message)} caractères)")
                    break
            
            # Soumettre le formulaire
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:has-text('Envoyer')",
                "button:has-text('Submit')",
                "input[value='Envoyer']"
            ]
            
            submitted = False
            for selector in submit_selectors:
                if page.query_selector(selector):
                    page.click(selector)
                    logger.info("🚀 Formulaire soumis")
                    submitted = True
                    break
            
            if not submitted:
                logger.warning("Bouton submit non trouvé, tentative avec Enter")
                page.keyboard.press("Enter")
            
            # Attendre la confirmation (message de succès ou redirection)
            try:
                page.wait_for_selector(
                    "text=/merci|thank you|envoyé|succès|success/i",
                    timeout=5000
                )
                logger.info("Confirmation reçue")
            except PlaywrightTimeout:
                logger.warning("Pas de message de confirmation visible (timeout)")
            
            # Fermer le navigateur
            browser.close()
            
            return f"""**Formulaire de contact soumis avec succès !**

📝 Informations envoyées :
- **Nom** : {name}
- **Email** : {email}
- **Sujet** : {subject}
- **Message** : {message[:100]}{'...' if len(message) > 100 else ''}

L'administration de l'IMT vous contactera prochainement.
"""
    
    except PlaywrightTimeout as e:
        logger.error(f"Timeout : {e}")
        return f"""**Erreur : Timeout lors du remplissage du formulaire**

Le site web de l'IMT n'a pas répondu à temps. Causes possibles :
- Connexion Internet lente
- Site web temporairement indisponible
- Formulaire protégé par CAPTCHA

**Alternative** : Vous pouvez contacter l'IMT directement par :
- Email : contact@imt.sn
- Téléphone : +221 33 859 73 73
"""
    
    except Exception as e:
        logger.error(f"Erreur Playwright : {e}")
        return f"""**Erreur lors du remplissage du formulaire**

Erreur technique : {str(e)}

**Alternative** : Contactez l'IMT directement :
- Email : contact@imt.sn
- Téléphone : +221 33 859 73 73
- Site web : https://www.imt.sn/contact/
"""


if __name__ == "__main__":
    # Test du formulaire
    logging.basicConfig(level=logging.INFO)
    
    result = fill_contact_form(
        name="Test Utilisateur",
        email="test@example.com",
        subject="Test automatique",
        message="Ceci est un test du formulaire automatique via Playwright.",
        phone="+221771234567"
    )
    
    print(result)
