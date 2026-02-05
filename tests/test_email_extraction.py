#!/usr/bin/env python3
import re

question1 = 'tu peux leur envoyer un mail disant que je suis entrain de tester mon bot IMT avec pour objet "essai 2" ?'
question2 = 'envoie un mail avec message "test extraction"'

for i, question in enumerate([question1, question2], 1):
    print(f"\n=== TEST {i} ===")
    print(f"Question: {question[:80]}...")
    
    # Test sujet
    subject_match = re.search(r'(?:avec|pour)\s+(?:comme\s+)?(?:pour\s+)?objet\s+["\']([^"\']+)["\']', question, re.IGNORECASE)
    subject = subject_match.group(1) if subject_match else "Demande d'informations"
    print(f"Sujet détecté: {subject}")
    
    # Test message
    message_match = re.search(r'(?:disant que|avec (?:comme )?message|message)\s+["\']?([^"\']+?)["\']?\s*(?:avec|pour|$)', question, re.IGNORECASE)
    if not message_match:
        message_match = re.search(r'(?:disant que|message[\s:]+)(.+?)(?:\s+avec|\s+pour|$)', question, re.IGNORECASE)
    
    content = message_match.group(1).strip() if message_match else question
    content = re.sub(r'\s*avec\s+pour\s+objet.+$', '', content, flags=re.IGNORECASE)
    print(f"Message détecté: {content}")
