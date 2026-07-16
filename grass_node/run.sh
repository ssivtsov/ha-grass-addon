#!/usr/bin/env bash
set -e

CONFIG_PATH=/data/options.json

USER_EMAIL="$(jq -r '.user_email // empty' "$CONFIG_PATH")"
USER_PASSWORD="$(jq -r '.user_password // empty' "$CONFIG_PATH")"
TRY_AUTOLOGIN_OPT="$(jq -r '.try_autologin // false' "$CONFIG_PATH")"
VNC_PASSWORD_OPT="$(jq -r '.vnc_password // empty' "$CONFIG_PATH")"
VNC_RESOLUTION_OPT="$(jq -r '.vnc_resolution // empty' "$CONFIG_PATH")"

# ---------------------------------------------------------------------------
# Persist the Grass desktop app's profile (login token) across restarts.
# HA add-on containers are recreated on every restart/update, so anything
# under /root is lost. /data is the only persistent location, so we move the
# app's config there (seeding from the image on first run) and symlink it back.
# This makes a manual login a one-time action instead of every restart.
# ---------------------------------------------------------------------------
PROFILE_DIR=/data/app-config
if [ ! -L /root/.config ]; then
    mkdir -p "$PROFILE_DIR"
    if [ -d /root/.config ]; then
        cp -a /root/.config/. "$PROFILE_DIR"/ 2>/dev/null || true
        rm -rf /root/.config
    fi
    ln -sfn "$PROFILE_DIR" /root/.config
fi
echo "[grass-node] Login profile persisted at /data/app-config (survives restarts)."

if [ -z "$USER_EMAIL" ] || [ -z "$USER_PASSWORD" ]; then
    echo "[grass-node] NOTE: user_email / user_password are not set."
    echo "[grass-node] Log in manually via the noVNC web UI (Web UI button / port 6080)."
fi

export USER_EMAIL
export USER_PASSWORD

# Auto-login is OFF by default: the upstream keystroke automation cannot type
# an email address (the '@'/'.' characters break its xdotool logic) and does
# not follow Grass's current email -> "Use Password Instead" -> password flow.
# Manual login through noVNC is the reliable path and, thanks to the profile
# persistence above, only needs to be done once.
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
echo "[grass-node] Open the Web UI (port 6080) to log in: enter email -> Continue -> 'Use Password Instead' -> password."

# Hand off to the upstream image's entrypoint chain, which starts the VNC
# server, noVNC and the Grass desktop application.
exec /usr/local/bin/customizable_entrypoint.sh
