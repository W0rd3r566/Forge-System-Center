#!/usr/bin/env bash
set -euo pipefail
APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ ! -x "$APP_DIR/.venv/bin/python" ]]; then
  echo "Forge is not installed yet. Run: bash install.sh" >&2
  exit 1
fi
exec "$APP_DIR/.venv/bin/python" "$APP_DIR/run.py" "$@"
