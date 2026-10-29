#!/usr/bin/env bash
set -euo pipefail
rm -f "$HOME/.local/bin/forge"
rm -f "$HOME/.local/share/applications/forge.desktop"
rm -f "$HOME/.local/share/icons/hicolor/scalable/apps/forge.svg"
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
fi
printf '%s\n' "Forge launcher removed. The project folder and .venv were kept." "Delete the project folder manually only if you are sure you no longer need it."
