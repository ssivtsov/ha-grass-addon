#!/usr/bin/env bash
set -e

CONFIG_PATH=/data/options.json

USER_EMAIL="$(jq -r '.user_email // empty' "$CONFIG_PATH")"
USER_PASSWORD="$(jq -r '.user_password // empty' "$CONFIG_PATH")"
TRY_AUTOLOGIN_OPT="$(jq -r '.try_autologin // true' "$CONFIG_PATH")"
EMAIL_XY_OPT="$(jq -r '.email_xy // empty' "$CONFIG_PATH")"
CONTINUE_XY_OPT="$(jq -r '.continue_xy // empty' "$CONFIG_PATH")"
USEPASS_XY_OPT="$(jq -r '.use_password_xy // empty' "$CONFIG_PATH")"
PASSWORD_XY_OPT="$(jq -r '.password_xy // empty' "$CONFIG_PATH")"
SIGNIN_XY_OPT="$(jq -r '.signin_xy // empty' "$CONFIG_PATH")"
DEBUG_SCREENSHOTS_OPT="$(jq -r '.debug_screenshots // false' "$CONFIG_PATH")"
VNC_PASSWORD_OPT="$(jq -r '.vnc_password // empty' "$CONFIG_PATH")"
VNC_RESOLUTION_OPT="$(jq -r '.vnc_resolution // empty' "$CONFIG_PATH")"

# ---------------------------------------------------------------------------
# Persist the Grass desktop app's profile (login token) across restarts.
# HA add-on containers are recreated on every restart/update, so anything
# under /root is lost. /data is the only persistent location, so we move the
# app's config there (seeding from the image on first run) and symlink it back.
# This makes a successful login (auto or manual) a one-time action.
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

# Auto-login uses our corrected entrypoint script (fixes email typing and
# follows Grass's email -> "Use Password Instead" -> password flow). If it
# misfires you can still log in manually via noVNC; the persisted profile
# means either way you only do it once.
if [ "$TRY_AUTOLOGIN_OPT" = "true" ]; then
    export TRY_AUTOLOGIN="true"
else
    export TRY_AUTOLOGIN="false"
fi

# Click targets ("x,y" offsets from the Grass window) for the login flow,
# tunable without a rebuild.
if [ -n "$EMAIL_XY_OPT" ]; then
    export EMAIL_XY="$EMAIL_XY_OPT"
fi
if [ -n "$CONTINUE_XY_OPT" ]; then
    export CONTINUE_XY="$CONTINUE_XY_OPT"
fi
if [ -n "$USEPASS_XY_OPT" ]; then
    export USEPASS_XY="$USEPASS_XY_OPT"
fi
if [ -n "$PASSWORD_XY_OPT" ]; then
    export PASSWORD_XY="$PASSWORD_XY_OPT"
fi
if [ -n "$SIGNIN_XY_OPT" ]; then
    export SIGNIN_XY="$SIGNIN_XY_OPT"
fi

# Save a screenshot of each login step to /data when enabled, for debugging.
if [ "$DEBUG_SCREENSHOTS_OPT" = "true" ]; then
    export DEBUG_SCREENSHOTS="true"
fi

if [ -n "$VNC_PASSWORD_OPT" ]; then
    export VNC_PASSWORD="$VNC_PASSWORD_OPT"
fi
if [ -n "$VNC_RESOLUTION_OPT" ]; then
    export VNC_RESOLUTION="$VNC_RESOLUTION_OPT"
fi

echo "[grass-node] Starting Grass desktop (email: ${USER_EMAIL:-<not set>}, autologin: ${TRY_AUTOLOGIN}, password_link_tabs: ${PASSWORD_LINK_TABS:-7})"
echo "[grass-node] Web UI on port 6080. Manual login: email -> Continue -> 'Use Password Instead' -> password."

# Hand off to the upstream image's entrypoint chain, which starts the VNC
# server, noVNC and the Grass desktop application (our corrected autologin).
exec /usr/local/bin/customizable_entrypoint.sh
