#!/usr/bin/env python3
# Test du système de détection de contenu inapproprié

from app.agent import _detect_inappropriate_content

print("=" * 60)
print("TEST DU SYSTÈME DE DÉTECTION DE CONTENU INAPPROPRIÉ")
print("=" * 60)

# Test 1 : Comparaisons
print("\nTest 1 : Comparaisons avec autres écoles")
print("-" * 60)
comparisons = [
    "IMT est meilleure que ESP",
    "Quelle école est meilleure entre IMT et UCAD?",
    "Comparez l'IMT avec l'EPT",
    "IMT vs ESP, laquelle choisir?",
]
for q in comparisons:
    result = _detect_inappropriate_content(q)
    status = "BLOQUÉ" if result else "RATÉ"
    print(f"{status} : {q}")

# Test 2 : Insultes
print("\nTest 2 : Insultes et dénigrement")
print("-" * 60)
insults = [
    "Votre école est nulle",
    "IMT c'est nul",
    "Formation pourrie",
    "C'est une arnaque",
]
for q in insults:
    result = _detect_inappropriate_content(q)
    status = "BLOQUÉ" if result else "RATÉ"
    print(f"{status} : {q}")

# Test 3 : Propos offensants
print("\nTest 3 : Propos offensants")
print("-" * 60)
offensive = [
    "ferme ta gueule",
    "va te faire",
    "tg",
]
for q in offensive:
    result = _detect_inappropriate_content(q)
    status = "BLOQUÉ" if result else "RATÉ"
    print(f"{status} : {q}")

# Test 4 : Questions normales (doivent PASSER)
print("\nTest 4 : Questions normales (doivent PASSER)")
print("-" * 60)
normal = [
    "Quelles sont les formations disponibles?",
    "Comment s'inscrire à l'IMT?",
    "Quel est le contact du directeur?",
    "Je m'appelle Maliki",
]
for q in normal:
    result = _detect_inappropriate_content(q)
    status = "PASSÉ" if not result else "BLOQUÉ À TORT"
    print(f"{status} : {q}")

# Test 5 : Afficher un message de refus exemple
print("\nExemple de message de refus (comparaison):")
print("-" * 60)
example = _detect_inappropriate_content("IMT est meilleure que ESP")
if example:
    print(example)

print("\n" + "=" * 60)
print("FIN DES TESTS")
print("=" * 60)