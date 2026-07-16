#!/usr/bin/env bash
set -e

CONFIG_PATH=/data/options.json

USER_EMAIL="$(jq -r '.user_email // empty' "$CONFIG_PATH")"
USER_PASSWORD="$(jq -r '.user_password // empty' "$CONFIG_PATH")"
VNC_PASSWORD_OPT="$(jq -r '.vnc_password // empty' "$CONFIG_PATH")"
VNC_RESOLUTION_OPT="$(jq -r '.vnc_resolution // empty' "$CONFIG_PATH")"
HEADLESS_OPT="$(jq -r '.headless // false' "$CONFIG_PATH")"
MAX_RETRY_MULTIPLIER_OPT="$(jq -r '.max_retry_multiplier // 3' "$CONFIG_PATH")"

if [ -z "$USER_EMAIL" ] || [ -z "$USER_PASSWORD" ]; then
    echo "[grass-node] WARNING: user_email / user_password are not set in the add-on configuration."
    echo "[grass-node] Automatic login will fail. You can still log in manually via the noVNC web UI (port 6080)."
fi

export USER_EMAIL
export USER_PASSWORD
export HEADLESS="$HEADLESS_OPT"
export MAX_RETRY_MULTIPLIER="$MAX_RETRY_MULTIPLIER_OPT"

if [ -n "$VNC_PASSWORD_OPT" ]; then
    export VNC_PASSWORD="$VNC_PASSWORD_OPT"
fi
if [ -n "$VNC_RESOLUTION_OPT" ]; then
    export VNC_RESOLUTION="$VNC_RESOLUTION_OPT"
fi

echo "[grass-node] Starting Grass node (email: ${USER_EMAIL:-<not set>}, headless: ${HEADLESS})"

# Hand off to the upstream image's entrypoint chain, which starts the VNC
# server, noVNC and the Grass extension login/monitor script.
exec /usr/local/bin/customizable_entrypoint.sh
