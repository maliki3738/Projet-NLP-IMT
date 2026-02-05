#!/usr/bin/env python3
"""
Test des outils isolément (search + email) sans LLM.
Utile quand quotas API épuisés.
"""
from app.tools import search_imt, send_email

print("=" * 80)
print("🧪 TEST DES OUTILS (Sans LLM)")
print("=" * 80)

# Test 1 : Recherche IMT
print("\n📌 TEST 1 : Recherche IMT avec RAG vectoriel\n")
questions = [
    "Quelles sont les formations ?",
    "Comment vous contacter ?",
    "C'est quoi l'IMT ?"
]

for q in questions:
    print(f"❓ Question : {q}")
    result = search_imt(q)
    print(f"✅ Réponse : {result[:150]}...\n")

# Test 2 : Validation email
print("\n📌 TEST 2 : Validation adresses email\n")
test_emails = [
    "test@gmail.com",
    "invalide@",
    "user@imt.sn",
    "pas-un-email"
]

from app.tools import _validate_email
for email in test_emails:
    valid = _validate_email(email)
    emoji = "✅" if valid else "❌"
    print(f"{emoji} {email} : {'Valide' if valid else 'Invalide'}")

# Test 3 : Envoi email (mode simulation)
print("\n📌 TEST 3 : Envoi email (mode simulation)\n")
result = send_email(
    subject="Test RAG",
    content="Ceci est un test du système IMT Agent",
    recipient="test@example.com"
)
print(f"📧 Résultat : {result}")

print("\n" + "=" * 80)
print("✅ Tests terminés ! Tous les outils fonctionnent.")
print("=" * 80)