#!/bin/bash
# GUNOUT — Lancement automatique (serveur POT + application)

set -e

POT_DIR="$HOME/bgutil-ytdlp-pot-provider/server"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Démarre le serveur POT en arrière-plan
echo "→ Démarrage du serveur POT..."
cd "$POT_DIR/node_modules"
deno run --allow-env --allow-net --allow-ffi=. --allow-read=. ../src/main.ts &
POT_PID=$!

# 2. Attendre que le serveur réponde
echo "→ Attente du serveur POT..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:4416/ping >/dev/null 2>&1; then
        echo "✓ Serveur POT prêt"
        break
    fi
    sleep 0.5
done

# 3. Lance l'application
echo "→ Lancement de GUNOUT..."
cd "$APP_DIR"
source app/bin/activate
python3 gunout.py

# 4. À la fermeture de l'app, tue le serveur POT
echo "→ Fermeture du serveur POT..."
kill $POT_PID 2>/dev/null || true
