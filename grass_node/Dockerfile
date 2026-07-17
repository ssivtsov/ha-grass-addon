ARG BUILD_FROM=mrcolorrain/grass-desktop:latest
FROM ${BUILD_FROM}

# Debian base; jq reads /data/options.json in run.sh, scrot captures optional
# debug screenshots of the login flow.
RUN apt-get update \
    && apt-get install -y --no-install-recommends jq scrot \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Replace the upstream autologin entrypoint script with our corrected version
# (fixes email typing via `xdotool type` and follows Grass's email-first login
# flow). The custom entrypoints directory holds a single *_main.py; overwrite
# it regardless of its exact filename.
COPY grass-desktop_main.py /tmp/grass-desktop_main.py
RUN set -e; \
    d=/app/custom_entrypoints_scripts; \
    f="$(ls "$d"/*.py 2>/dev/null | head -n1)"; \
    if [ -n "$f" ]; then \
        cp /tmp/grass-desktop_main.py "$f"; \
        echo "Replaced autologin script: $f"; \
    else \
        echo "WARNING: no custom entrypoint *.py found in $d; leaving image as-is"; \
    fi; \
    rm -f /tmp/grass-desktop_main.py

COPY run.sh /run.sh
RUN chmod +x /run.sh

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/run.sh"]
