#!/bin/sh
set -e

CONFIG_PATH=/data/options.json

USER_EMAIL="$(jq -r '.user_email // empty' "$CONFIG_PATH")"
USER_PASSWORD="$(jq -r '.user_password // empty' "$CONFIG_PATH")"
ALLOW_DEBUG_OPT="$(jq -r '.allow_debug // false' "$CONFIG_PATH")"

if [ -z "$USER_EMAIL" ] || [ -z "$USER_PASSWORD" ]; then
    echo "[grass-node] ERROR: user_email / user_password are not set in the add-on configuration."
    echo "[grass-node] Set them in the Configuration tab and restart the add-on."
    exit 1
fi

export GRASS_USER="$USER_EMAIL"
export GRASS_PASS="$USER_PASSWORD"
if [ "$ALLOW_DEBUG_OPT" = "true" ]; then
    export ALLOW_DEBUG="True"
else
    export ALLOW_DEBUG="False"
fi

echo "[grass-node] Starting Grass node (email: ${USER_EMAIL})"
echo "[grass-node] Status page will be available on the mapped port (Web UI button)."

cd /usr/src/app
exec python ./main.py
