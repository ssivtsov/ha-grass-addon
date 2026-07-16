#!/bin/sh
# Wrapper so Selenium Manager finds a "google-chrome" binary and uses the
# system Chromium with the flags required to run stably in a container
# (no GPU, single renderer process, no sandbox).
exec /usr/bin/chromium \
  --no-sandbox \
  --disable-setuid-sandbox \
  --disable-gpu \
  --disable-software-rasterizer \
  --disable-dev-shm-usage \
  --single-process \
  "$@"
