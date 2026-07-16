# Changelog

## 1.0.5

- Re-add minimal Python patch alongside the `google-chrome.sh` wrapper.
  `SE_DRIVER_LOCATION` env var is not honoured by the Selenium version in
  the base image. The patch wires `binary_location` to the wrapper and
  uses an explicit `ChromeService('/usr/bin/chromedriver')` — the only
  reliable way to bypass Selenium Manager's automatic (and failing) driver
  discovery in this environment.

## 1.0.4

- Replace Python script patching with a clean shell wrapper (`google-chrome.sh`
  installed as `/usr/local/bin/google-chrome`). Selenium Manager finds the
  wrapper on PATH, which calls the system Chromium with all required container
  flags (`--no-sandbox`, `--disable-setuid-sandbox`, `--disable-gpu`,
  `--disable-software-rasterizer`, `--disable-dev-shm-usage`,
  `--single-process`). System chromedriver is pointed at via `SE_DRIVER_LOCATION`
  env var, bypassing any internet download attempt.

## 1.0.3

- Fix Chromium crash during page navigation in containerised environments
  (`Error during login: Message: ` with raw stacktrace). Add
  `--disable-gpu` and `--disable-software-rasterizer` Chrome flags via the
  build-time patch; these are required when no GPU hardware is available.

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
