#!/bin/sh
set -e

echo "→ Application des migrations…"
python manage.py migrate --noinput

if [ "${RUN_SEED:-false}" = "true" ]; then
    echo "→ Chargement des données de base (niveaux 1-9, matières)…"
    python manage.py seed
fi

exec "$@"