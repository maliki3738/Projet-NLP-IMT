#!/bin/bash
# Script simple pour lancer l'agent IMT avec Chainlit

cd /Users/mac/Desktop/NLP/Projet/imt-agent-clean
source venv/bin/activate
chainlit run chainlit_app.py -w
