#!/usr/bin/env bash
# Wrapper that adds required container flags and delegates to system Chromium.
exec /usr/bin/chromium \
    --no-sandbox \
    --disable-setuid-sandbox \
    --disable-gpu \
    --disable-software-rasterizer \
    --disable-dev-shm-usage \
    "$@"
