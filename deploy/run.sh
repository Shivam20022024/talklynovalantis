#!/bin/bash
# Build and (re)start the whole stack (backend + frontend) via docker-compose.
# Run from the repo root after ec2-setup.sh has installed Docker and both
# backend/.env.local and .env (NEXT_PUBLIC_API_URL) have been created.
#
# For backend-only deploys (no frontend container), use
# backend/deploy/run.sh instead.
set -euo pipefail
cd "$(dirname "$0")/.."

docker compose up -d --build

echo "Backend running on :8000, frontend on :3000."
echo "Logs: docker compose logs -f"
