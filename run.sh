#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi
echo "Applying migrations..."
python manage.py migrate --noinput
echo "Starting dev server on 0.0.0.0:8000"
python manage.py runserver 0.0.0.0:8000
