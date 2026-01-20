@echo off
echo ===========================================
echo  Démarrage de l'Agent IMT Dakar
echo ===========================================
echo.

echo [1/2] Démarrage de Redis...
start "" "%~dp0redis\redis-server.exe"

echo Attente du démarrage de Redis...
timeout /t 3 /nobreak > nul

echo [2/2] Démarrage de l'application Chainlit...
chainlit run chainlit_app.py

echo.
echo ===========================================
echo  Application arrêtée
echo ===========================================