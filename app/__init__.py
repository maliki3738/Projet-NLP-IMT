"""Package `app` pour le projet imt-agent-clean.

Ce fichier permet à Python de reconnaître le dossier `app` comme un package
et autorise des imports tels que `import app.tools` lorsqu'on exécute
`python app/agent.py` depuis la racine du projet.
"""

__all__ = ["tools", "agent"]
