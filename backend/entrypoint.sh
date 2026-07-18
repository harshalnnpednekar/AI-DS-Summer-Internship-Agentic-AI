#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

if [ "${SEED_ON_STARTUP}" = "true" ]; then
  echo "Seeding database..."
  python -m app.seed
fi

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
