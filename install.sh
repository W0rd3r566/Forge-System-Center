#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3 was not found. Install Python 3.10 or newer, then run this installer again."
  exit 1
fi
if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
  echo "Forge requires Python 3.10 or newer. Detected: $("$PYTHON_BIN" --version 2>&1)"
  exit 1
fi

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This installer creates a Linux desktop entry. On Windows, run install.ps1 instead."
  exit 1
fi

echo "Forge installer"
echo "Project: $APP_DIR"
echo "Python:  $("$PYTHON_BIN" --version 2>&1)"
echo
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  case "${ID:-}" in
    debian|ubuntu|linuxmint|pop)
      echo "Debian/Ubuntu Qt runtime packages may be required:"
      echo "  sudo apt install libegl1 libgl1 libxkbcommon-x11-0 libdbus-1-3 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-shape0 libxcb-xinerama0"
      ;;
    arch|cachyos|manjaro|endeavouros)
      echo "Arch/CachyOS Qt runtime packages may be required:"
      echo "  sudo pacman -S --needed libxcb xcb-util-cursor libxkbcommon mesa libglvnd fontconfig freetype2 dbus"
      ;;
  esac
fi
echo
echo "This downloads PySide6 and psutil into an isolated .venv. It will not use sudo or modify system packages."
read -r -p "Continue? [Y/n] " answer
if [[ "$answer" =~ ^[Nn]$ ]]; then
  echo "Cancelled. No changes were made."
  exit 0
fi

if [[ ! -d "$APP_DIR/.venv" ]]; then
  "$PYTHON_BIN" -m venv "$APP_DIR/.venv"
fi
"$APP_DIR/.venv/bin/python" -m pip install --upgrade pip
"$APP_DIR/.venv/bin/python" -m pip install -r "$APP_DIR/requirements.txt"
"$APP_DIR/.venv/bin/python" -c 'import PySide6, psutil; print("PySide6", PySide6.__version__); print("psutil", psutil.__version__)'

BIN_DIR="$HOME/.local/bin"
APP_ENTRY_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
mkdir -p "$BIN_DIR" "$APP_ENTRY_DIR" "$ICON_DIR"

cat > "$BIN_DIR/forge" <<EOF
#!/usr/bin/env bash
set -euo pipefail
exec "$APP_DIR/.venv/bin/python" "$APP_DIR/run.py" "\$@"
EOF
chmod +x "$BIN_DIR/forge"
cp "$APP_DIR/assets/forge.svg" "$ICON_DIR/forge.svg"
cat > "$APP_ENTRY_DIR/forge.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Forge System Center
Comment=Local desktop system dashboard
Exec=$BIN_DIR/forge
Icon=forge
Terminal=false
Categories=System;Monitor;
StartupNotify=true
EOF
chmod 644 "$APP_ENTRY_DIR/forge.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$APP_ENTRY_DIR" >/dev/null 2>&1 || true
fi

echo
echo "Forge installed. Launch it from your application menu or run: $BIN_DIR/forge"
echo "To run from this directory at any time: bash run.sh"
echo "Your data and settings are not uploaded anywhere."
