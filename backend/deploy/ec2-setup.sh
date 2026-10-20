#!/bin/bash
# Run this once, interactively, after SSH-ing into a fresh EC2 instance
# (Ubuntu 22.04/24.04 LTS AMI, ap-south-1). Installs Docker, Nginx and Certbot.
# Does NOT clone the repo or touch secrets — that happens after this script.
set -euo pipefail

sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg nginx

# Docker Engine + Compose plugin (official Docker repo)
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

sudo usermod -aG docker "$USER"

echo "Done. Log out and back in (or run 'newgrp docker') for the docker group to take effect."
echo "Next: git clone your repo, create backend/.env.local, then run backend/deploy/run.sh"
