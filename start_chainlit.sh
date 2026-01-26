#!/bin/bash

# Script de lancement Chainlit pour imt-agent-clean
# Résout les problèmes d'environnement et de démarrage

cd "$(dirname "$0")"

VENV_PATH="./venv/bin"

# Vérifier si venv existe
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Environnement virtuel introuvable"
    exit 1
fi

# Kill processus chainlit existants
pkill -f "chainlit run" 2>/dev/null || true
sleep 1

echo "🚀 Lancement de Chainlit..."
echo "📂 Dossier: $(pwd)"
echo "🐍 Python: $VENV_PATH/python"

# Lancer Chainlit
export TOKENIZERS_PARALLELISM=false
exec "$VENV_PATH/python" -m chainlit run chainlit_app.py --port 8000
