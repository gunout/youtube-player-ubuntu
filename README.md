<div align="center">

# GUNOUT

**Lecteur YouTube open source pour Ubuntu — léger, épuré, sans publicité.**

Interface frameless en verre dépoli · Lecture native via mpv · Recherche propulsée par yt-dlp

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.x-41CD52?logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Ubuntu-E95420?logo=ubuntu&logoColor=white)](https://ubuntu.com/)

</div>

---

## ✨ Fonctionnalités

- **Interface épurée** — fenêtre frameless, coins arrondis, zéro bordure visible
- **Lecture native** — vidéo intégrée via `libmpv` (pas de tracking Google, pas de pub)
- **Recherche instantanée** — résultats en overlay, sans figer l'interface (thread séparé)
- **Contrôles complets** — play/pause, seek, volume, mute, plein écran
- **Deux modes de replis** — la barre de contrôles ou toute la fenêtre
- **Auto-hide** — les contrôles disparaissent après 3 s d'inactivité
- **Redimensionnable** — bords et coins sensibles à la souris, drag & drop intégré
- **Support URL directe** — colle un lien YouTube et la lecture démarre
- **Signature discrète** — `by gleaphe`

## 📸 Aperçu

> _Ajoute ici une capture d'écran de l'application._
> `![Aperçu de GUNOUT](docs/screenshot.png)`

## 🎬 Démo

> _Ajoute ici un GIF ou une courte vidéo de démonstration._
> `![Démo](docs/demo.gif)`

## 🧱 Architecture

```
gunout/
├── gunout.py              # Application principale
├── requirements.txt       # Dépendances Python
├── launch.sh              # Script de lancement (démarre le serveur POT + l'app)
└── README.md
```

**Stack technique :**

| Composant | Rôle |
|-----------|------|
| **PyQt6** | Interface graphique |
| **python-mpv** | Lecture vidéo native via `libmpv` |
| **yt-dlp** | Extraction des flux YouTube |
| **bgutil-ytdlp-pot-provider** | Génération des jetons PO (contourne les restrictions YouTube) |
| **Deno** | Exécution du serveur POT |

## 🚀 Installation

### Prérequis

- Ubuntu 22.04+ (ou toute distro avec les mêmes paquets)
- Python 3.10+
- `mpv` et `libmpv-dev` installés

### Étape 1 — Dépendances système

```bash
sudo apt update
sudo apt install python3-pip mpv libmpv-dev git curl
```

### Étape 2 — Cloner le dépôt

```bash
git clone https://github.com/gleaphe/youtube-player-ubuntu.git
cd youtube-player-ubuntu
```

### Étape 3 — Environnement virtuel Python

```bash
python3 -m venv app
source app/bin/activate
pip install -r requirements.txt
```

### Étape 4 — Installer Deno (pour le serveur POT)

```bash
curl -fsSL https://deno.land/install.sh | sh
source ~/.zshrc   # ou ~/.bashrc
deno --version
```

### Étape 5 — Installer le serveur POT

```bash
cd ~
git clone --single-branch --branch 2.0.0 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git
cd bgutil-ytdlp-pot-provider/server/
deno install --allow-scripts=npm:canvas --frozen
```

### Étape 6 — Plugin Python pour yt-dlp

```bash
cd ~/youtube-player-ubuntu
source app/bin/activate
pip install bgutil-ytdlp-pot-provider
```

## 🎮 Utilisation

### Lancement manuel (deux terminaux)

**Terminal 1 — Serveur POT** (à laisser ouvert) :

```bash
cd ~/bgutil-ytdlp-pot-provider/server/node_modules
deno run --allow-env --allow-net --allow-ffi=. --allow-read=. ../src/main.ts
```

**Terminal 2 — Application** :

```bash
cd ~/youtube-player-ubuntu
source app/bin/activate
python3 gunout.py
```

### Lancement automatique (script)

```bash
chmod +x launch.sh
./launch.sh
```

## 🕹️ Raccourcis & interactions

| Action | Comment |
|--------|---------|
| Rechercher | Tape dans la barre du haut, appuie sur **Entrée** |
| Coller une URL | Colle `https://youtube.com/watch?v=...` puis **Entrée** |
| Lire une vidéo | **Double-clic** sur un résultat |
| Déplacer la fenêtre | **Clic-glisse** au centre |
| Redimensionner | **Clic-glisse** sur un bord ou un coin |
| Replier les contrôles | Bouton **⌃** dans la barre de contrôles |
| Replier la fenêtre | Bouton **⌃** en haut à droite |
| Plein écran | Bouton **⛶** |
| Quitter | Bouton **✕** |

## ⚙️ Configuration

Les paramètres sont en haut de `gunout.py` :

```python
# Palette
ACCENT = "#00e5ff"      # Couleur d'accent
BG     = "rgba(12, 12, 14, 240)"  # Fond de fenêtre

# Auto-hide
self.hide_timer.setInterval(3000)   # 3 secondes

# Hauteur repliée
def _folded_height(self):
    return 90   # px
```

## 🐛 Dépannage

### Les recherches renvoient 0 résultat

Le serveur POT n'est pas lancé ou n'est pas détecté.

```bash
# Vérifier que le serveur répond
curl http://127.0.0.1:4416/ping
```

Si rien ne répond, relance le serveur (voir étape 5).

### La vidéo est noire

Teste avec X11 forcé :

```bash
QT_QPA_PLATFORM=xcb python3 gunout.py
```

Ou change `vo='gpu'` en `vo='gpu-next'` dans `gunout.py`.

### Erreur `libmpv.so not found`

```bash
sudo apt install libmpv-dev
```

### L'interface rame

- Vérifie que `hwdec='auto-safe'` est bien dans les options mpv
- Ferme les autres applications gourmandes
- Essaie `vo='x11'` si `gpu` ne fonctionne pas

### Wayland : drag/resize saccadé

Lance avec :

```bash
QT_QPA_PLATFORM=xcb python3 gunout.py
```

## 🗺️ Feuille de route

- [x] Interface épurée frameless
- [x] Lecture native via mpv
- [x] Recherche en thread séparé
- [x] Contrôles complets
- [x] Replis contrôles + fenêtre
- [x] Auto-hide
- [ ] Thèmes clair/sombre
- [ ] Historique et favoris (SQLite)
- [ ] SponsorBlock
- [ ] Playlists
- [ ] Packaging `.deb` / AppImage

## 🤝 Contribution

Les contributions sont bienvenues. Pour proposer une amélioration :

1. Fork le dépôt
2. Crée une branche (`git checkout -b feature/ma-feature`)
3. Commit (`git commit -m 'Ajoute ma feature'`)
4. Push (`git push origin feature/ma-feature`)
5. Ouvre une Pull Request

## 📜 Licence

Distribué sous licence **MIT**. Voir [`LICENSE`](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — extraction YouTube
- [mpv](https://mpv.io/) — moteur de lecture
- [bgutil-ytdlp-pot-provider](https://github.com/Brainicism/bgutil-ytdlp-pot-provider) — jetons PO
- [PyQt6](https://pypi.org/project/PyQt6/) — framework UI

---

<div align="center">

**GUNOUT** — _by gleaphe_

Si ce projet t'est utile, n'hésite pas à lui donner une ⭐

</div>
