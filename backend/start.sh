#!/usr/bin/env bash
see set -e

# Create directories
mkdir -p uploads instance

# Check PORT variable
if [ -z "$PORT" ]; then
  export PORT=10000
fi

echo "Starting on port $PORT"

# Start gunicorn
exec gunicorn app:app \
  --bind 0.0.0.0:$PORT \
  --workers 1 \
  --threads 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level debug
