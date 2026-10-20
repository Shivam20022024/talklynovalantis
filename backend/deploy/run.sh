#!/bin/bash
# Build and (re)start the backend container. Run from backend/ after
# ec2-setup.sh has installed Docker and backend/.env.local has been created.
set -euo pipefail
cd "$(dirname "$0")/.."

docker build -t talkly-backend .

docker rm -f talkly-backend 2>/dev/null || true

docker run -d \
  --name talkly-backend \
  --restart unless-stopped \
  --env-file .env.local \
  -p 8000:8000 \
  talkly-backend

echo "Backend running on port 8000. Check logs with: docker logs -f talkly-backend"
