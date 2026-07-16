#!/usr/bin/env bash
set -e

CONFIG_PATH=/data/options.json

USER_EMAIL="$(jq -r '.user_email // empty' "$CONFIG_PATH")"
USER_PASSWORD="$(jq -r '.user_password // empty' "$CONFIG_PATH")"
TRY_AUTOLOGIN_OPT="$(jq -r '.try_autologin // true' "$CONFIG_PATH")"
VNC_PASSWORD_OPT="$(jq -r '.vnc_password // empty' "$CONFIG_PATH")"
VNC_RESOLUTION_OPT="$(jq -r '.vnc_resolution // empty' "$CONFIG_PATH")"

if [ -z "$USER_EMAIL" ] || [ -z "$USER_PASSWORD" ]; then
    echo "[grass-node] NOTE: user_email / user_password are not set."
    echo "[grass-node] You can still log in manually via the noVNC web UI (Web UI button / port 6080)."
fi

export USER_EMAIL
export USER_PASSWORD

# The Grass desktop app auto-login can fail if Grass shows a CAPTCHA or
# changes its login flow. In that case set try_autologin=false (or just
# leave it on) and complete the login by hand through the noVNC web UI.
if [ "$TRY_AUTOLOGIN_OPT" = "true" ]; then
    export TRY_AUTOLOGIN="true"
else
    export TRY_AUTOLOGIN="false"
fi

if [ -n "$VNC_PASSWORD_OPT" ]; then
    export VNC_PASSWORD="$VNC_PASSWORD_OPT"
fi
if [ -n "$VNC_RESOLUTION_OPT" ]; then
    export VNC_RESOLUTION="$VNC_RESOLUTION_OPT"
fi

echo "[grass-node] Starting Grass desktop (email: ${USER_EMAIL:-<not set>}, autologin: ${TRY_AUTOLOGIN})"
echo "[grass-node] Open the Web UI (port 6080) to watch the app or log in manually."

# Hand off to the upstream image's entrypoint chain, which starts the VNC
# server, noVNC and the Grass desktop application.
exec /usr/local/bin/customizable_entrypoint.sh
