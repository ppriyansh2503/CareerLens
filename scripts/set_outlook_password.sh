#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"
BACKEND_ENV_FILE="$ROOT_DIR/backend/.env"

export PATH="$PATH:/Users/priyanshu/.docker/bin:/opt/homebrew/bin:/usr/local/bin"

echo "============================================================"
echo " CareerLens Outlook SMTP App Password Setup"
echo " Account: careerlens.platform@outlook.com"
echo "============================================================"
echo ""

printf "Enter Outlook App Password (typing hidden): "
read -s RAW_PASS
echo ""

# Remove any spaces in app password (Microsoft presents them as 4 groups of 4 characters)
APP_PASS="$(echo -n "$RAW_PASS" | tr -d '[:space:]')"

if [ -z "$APP_PASS" ]; then
    echo "Error: Password cannot be empty."
    exit 1
fi

# Update .env
if grep -q "^SMTP_PASSWORD=" "$ENV_FILE"; then
    sed -i '' "s|^SMTP_PASSWORD=.*|SMTP_PASSWORD=$APP_PASS|" "$ENV_FILE"
else
    echo "SMTP_PASSWORD=$APP_PASS" >> "$ENV_FILE"
fi

# Update backend/.env
if [ -f "$BACKEND_ENV_FILE" ]; then
    if grep -q "^SMTP_PASSWORD=" "$BACKEND_ENV_FILE"; then
        sed -i '' "s|^SMTP_PASSWORD=.*|SMTP_PASSWORD=$APP_PASS|" "$BACKEND_ENV_FILE"
    else
        echo "SMTP_PASSWORD=$APP_PASS" >> "$BACKEND_ENV_FILE"
    fi
fi

echo ""
echo "-> App password saved to local .env (protected and gitignored)."
echo "-> Restarting Docker backend container..."

docker compose up -d backend

echo ""
echo "-> Docker backend successfully restarted with Outlook SMTP configuration!"
echo "============================================================"
