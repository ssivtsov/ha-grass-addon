# Changelog

## 1.0.2

- Fix startup failure `Error initializing WebDriver: Unable to obtain driver
  for chrome`. The upstream script relies on Selenium Manager auto-discovery,
  which cannot find Debian's chromium/chromedriver; the add-on now installs
  `chromium` and `chromium-driver` explicitly and patches the script at build
  time to use explicit binary/driver paths (overridable via `CHROME_BIN` /
  `CHROMEDRIVER_BIN`).

## 1.0.1

- Make `vnc_password`, `vnc_resolution`, `headless` and `max_retry_multiplier`
  optional in the configuration schema. Only `user_email` and `user_password`
  are required; removed options fall back to the upstream image defaults
  (VNC password `money4band`, resolution `1280x720`, headless off,
  retry multiplier 3).

## 1.0.0

- Initial release.
- Wraps the multi-arch `mrcolorrain/grass-node` image (amd64 / aarch64).
- Configurable via add-on options: Grass account email and password, VNC
  password, VNC resolution, headless mode, retry backoff multiplier.
- noVNC web UI on port 6080 and VNC on port 5900.
