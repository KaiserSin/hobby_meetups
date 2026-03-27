#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required but was not found."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
# shellcheck disable=SC1091
source .venv/bin/activate

echo "Installing Flask..."
python -m pip install --upgrade pip
python -m pip install Flask

echo "Initializing database..."
python - <<'PY'
from app import create_app

create_app()
print("Database initialized.")
PY

echo "Starting server at http://127.0.0.1:5000"
python app.py
