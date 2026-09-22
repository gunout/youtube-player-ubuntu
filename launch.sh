#!/bin/bash
# GUNOUT — Lancement automatique (serveur POT + application)

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Auto-détection du serveur POT ---
POT_DIR=""
for candidate in "$HOME/bgutil-ytdlp-pot-provider/server" \
                 "$HOME/Desktop/bgutil-ytdlp-pot-provider/server" \
                 "$HOME/Documents/bgutil-ytdlp-pot-provider/server" \
                 "$HOME/Téléchargements/bgutil-ytdlp-pot-provider/server"; do
    if [ -d "$candidate/node_modules" ]; then
        POT_DIR="$candidate"
        break
    fi
done

if [ -z "$POT_DIR" ]; then
    echo "❌ Serveur POT introuvable."
    echo "   Clone-le d'abord :"
    echo "   git clone --single-branch --branch 2.0.0 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git"
    exit 1
fi

# 1. Démarre le serveur POT en arrière-plan
echo "→ Démarrage du serveur POT depuis $POT_DIR"
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
