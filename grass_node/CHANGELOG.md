# Changelog

## 1.0.11

- Chromium crash after 30 seconds of page loading: `--no-zygote` (added
  in 1.0.10) interferes with renderer processes and extension loading —
  removed. Reduce injected flags to the minimal set that prevents GPU
  crashes: `--disable-gpu` and `--disable-software-rasterizer` only. The
  upstream script already sets the sandbox and /dev/shm flags itself.

## 1.0.10

- Chromium crash (`Connection refused` / raw stacktrace) after session
  creation: add required container flags (`--no-sandbox`,
  `--disable-setuid-sandbox`, `--disable-gpu`, `--disable-software-rasterizer`,
  `--disable-dev-shm-usage`, `--no-zygote`) directly to `ChromeOptions` via
  the prepend patch so they are applied by chromedriver regardless of the
  binary path chain.

## 1.0.9

- Replace `sitecustomize.py` (which was silently not loading in this image)
  with a build-time prepend to `grass-node_main.py`. The monkeypatch is
  written to the top of the upstream script during `docker build` — no path
  discovery, no try/except hiding failures. Patches `_wd.Chrome.__init__`
  via method replacement so it works regardless of how the script calls
  `webdriver.Chrome()`.

## 1.0.8

- Replace `patch-webdriver.py` (fragile regex source patching) with
  `sitecustomize.py`. Python automatically imports `sitecustomize` before
  any user script, so this patches `selenium.webdriver.Chrome` at the class
  level regardless of how the upstream script calls it — no source inspection
  required. Sets explicit `ChromeService('/usr/bin/chromedriver')` and
  `binary_location='/usr/local/bin/google-chrome'` on every Chrome instance.

## 1.0.7

- Restore ChromeService patch and `google-chrome.sh` wrapper (removed in
  1.0.6). `full_access: true` fixes container privilege issues but does not
  help Selenium Manager locate Debian's chromedriver — explicit
  `ChromeService('/usr/bin/chromedriver')` and `binary_location` are still
  required. Also installs `chromium` and `chromium-driver` explicitly so the
  paths are guaranteed to exist.

## 1.0.6

- Switch to `full_access: true` in the addon config. This runs the
  upstream `mrcolorrain/grass-node` image with full host privileges
  (equivalent to `docker run --privileged`), which lets Selenium and
  Chromium work in HA's container environment without any patches or
  wrapper scripts. Removes `patch-webdriver.py` and `google-chrome.sh`.
  Note: HA will show a security warning for this addon because of the
  elevated privileges.
- Fix the Web UI link: point `webui` to `/vnc.html` so the HA "Open Web
  UI" button lands directly on the noVNC viewer instead of the directory
  listing.

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
