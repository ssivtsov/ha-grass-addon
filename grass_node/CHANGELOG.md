# Changelog

## 2.1.9

- **Eliminate 45-second delay when CDP is unavailable.** The `/usr/bin/grass`
  wrapper does not forward `--remote-debugging-port` to the Electron binary, so
  the Chrome DevTools Protocol endpoint never opens. Previously each of the three
  button clicks (CONTINUE, Use Password Instead, SIGN IN) would wait 15 s for a
  DOM element before falling back to the coordinate click, adding ~45 s to every
  login. Now: after the initial 30 s CDP readiness check fails, all subsequent
  CDP calls return immediately and the coordinate fallback is used without delay.

## 2.1.8

- **Fix SIGN IN coordinate on the password screen.** The password screen has a
  different layout to the email screen: "Forgot Password?" sits at y≈284 and the
  SIGN IN button is at y≈340.  The previous default `signin_xy: "175,296"` hit
  "Forgot Password?" instead of SIGN IN.  Default corrected to `"175,340"`.
  (CDP fell back to coordinates in v2.1.7 because `/usr/bin/grass` does not
  forward `--remote-debugging-port` to the Electron binary; the coordinate
  fallback path now has all four positions correct.)

## 2.1.7

- **DOM-based button clicks via Chrome DevTools Protocol (CDP).** The Grass
  desktop app is an Electron/Chromium application; launching it with
  `--remote-debugging-port` exposes a CDP endpoint. The autologin script now
  connects to that endpoint and clicks CONTINUE, "Use Password Instead" and
  SIGN IN by finding the elements in the DOM by their visible text, rather
  than relying on fixed screen coordinates. This makes those steps immune to
  window position and resolution changes.  Coordinate-based clicks are kept
  as a fallback in case the CDP endpoint is unavailable.
- Install `python3-websocket` (Debian package for `websocket-client`) in the
  Dockerfile so the CDP WebSocket connection is available without pip.
- `use_password_xy` default corrected to `"175,475"` (was `"175,440"`) for
  the coordinate fallback path.

## 2.1.6

- **Fix "Use Password Instead" click position.** Screenshots confirmed the link
  is at window-relative y≈475, not y=440 as set in 2.1.5. Default
  `use_password_xy` updated from `"175,440"` to `"175,475"`. Users who already
  set a custom value are unaffected.

## 2.1.5

- **Auto-login now clicks fields/buttons instead of Tab navigation.** The
  debug screenshots showed the email field was never focused (so `Ctrl+A`
  selected the whole page and the email was not entered), and the blind
  `Tab → Return` closed the login window by hitting its ✕ button. The script
  now moves the mouse and clicks the email field, CONTINUE, "Use Password
  Instead", the password field and SIGN IN at known positions.
- **New tunable click positions** (`email_xy`, `continue_xy`,
  `use_password_xy`, `password_xy`, `signin_xy`) as `"x,y"` offsets from the
  Grass window, so they can be corrected from the debug screenshots without a
  rebuild. Replaces the previous `*_tabs` options (kept as ignored no-ops).

## 2.1.4

- **Debug screenshots now go to `/share/grass-debug/`** instead of the
  add-on's private `/data`, so they can be browsed with the File editor,
  Samba, or Studio Code Server add-ons. Maps `share:rw`. Falls back to
  `/data` if `/share` is not available.

## 2.1.3

- **Fix auto-login getting stuck on the email screen.** Grass's login form
  does not submit on Enter — the CONTINUE / SIGN IN buttons must be focused
  and activated. Previously pressing Return in the email field did nothing,
  so the flow never advanced and the password ended up typed into the email
  field. Now the script Tabs to CONTINUE (and to SIGN IN) and presses Return
  to click them, and clears each field before typing.
- **New tunable tab counts:** `continue_tabs` (default 1) and `signin_tabs`
  (default 1), alongside the existing `password_link_tabs` (default 7).
- **New `debug_screenshots` option:** saves a screenshot of each login step
  to `/data/grass-step*.png` (via `scrot`) so the exact app state at each
  keystroke can be inspected.

## 2.1.2

- **Fix auto-login.** Ships a corrected entrypoint script that replaces the
  upstream one:
  - Credentials are now always typed with `xdotool type` (with `--`), so an
    email like `user@gmail.com` is entered into the field instead of being
    rejected as an `Invalid key sequence` by `xdotool key`.
  - The login choreography follows Grass's current flow: type email →
    Return (Continue) → Tab to "Use Password Instead" → Return → type
    password → Return (Sign In).
- **New `password_link_tabs` option** (default 7): how many Tab presses reach
  the "Use Password Instead" link. Tune it (watching noVNC) if auto-login
  lands on the wrong element — no rebuild needed.
- **Auto-login on by default again** now that it types credentials correctly.
  If it still misfires against a Grass UI change, manual login via noVNC
  works and the profile persistence added in 2.1.1 means either path is a
  one-time action.

## 2.1.1

- **Persist the login across restarts.** The Grass desktop app's profile
  (which holds the login token) now lives on `/data` instead of the
  throwaway container filesystem, so a manual login only needs to be done
  once — it survives add-on restarts and updates.
- **Auto-login off by default.** The upstream keystroke automation can't
  type an email address — it feeds the whole string to `xdotool key`, which
  rejects the `@`/`.` characters (`Invalid key sequence`) — and it doesn't
  follow Grass's current email → "Use Password Instead" → password flow.
  Manual login through noVNC is now the default and, with the persistence
  above, is a one-time action. `try_autologin` can still be set to `true`.
- Clearer log guidance on the exact manual login steps.

## 2.1.0

- **Switch to the real Grass desktop app** via
  [`mrcolorrain/grass-desktop`](https://hub.docker.com/r/mrcolorrain/grass-desktop),
  running inside noVNC. Both browser-automation images (`grass-node` and
  `autonomylabxyz/grass`) failed at the same point — loading the Grass
  login form — because Grass now blocks automated headless logins on its
  login page. Running the genuine desktop app sidesteps that: it attempts
  auto-login, and if that fails you log in **manually** through the noVNC
  web UI, after which the session persists.
- **Web UI is noVNC again** on port 6080 (VNC on 5900). The Web UI button
  opens `/vnc.html` directly.
- **Options:** `try_autologin` (default on) toggles the auto-login attempt;
  `user_email`/`user_password` are now optional (leave blank to log in
  entirely by hand); `vnc_password`/`vnc_resolution` are back.
- **amd64 only:** the Grass desktop app is an x86 Electron app, so this
  version targets `amd64`. (ARM hosts can't run the desktop app.)
- `full_access` re-enabled so the desktop app runs like a plain
  `docker run` — HA will show a security warning.

## 2.0.0

- **Switch upstream image** from `mrcolorrain/grass-node` to
  [`autonomylabxyz/grass`](https://github.com/autonomylab-xyz/grass). The
  1.x image's Selenium login consistently timed out waiting for the Grass
  login page in HA's environment. The new image runs headless Chromium with
  the Grass extension, uses an explicit chromedriver fallback (no Selenium
  Manager), and needs no patches or wrapper scripts at all.
- **Web UI replaced:** instead of noVNC/VNC (ports 6080/5900), the add-on now
  serves a small status page on port 8080 with connection state, network
  quality and earnings.
- **New option:** `allow_debug` — on login failure, upload a screenshot and
  browser log to a public image host for troubleshooting (off by default).
- **Deprecated options:** `vnc_password`, `vnc_resolution`, `headless`,
  `max_retry_multiplier` are now ignored and can be removed from the
  configuration.
- `full_access` privilege is no longer required and has been removed —
  the security warning in HA disappears.

## 1.0.12

- Remove `binary_location` / `google-chrome.sh` wrapper from the patch.
  The Debian `chromium` and `chromium-driver` packages are version-matched;
  chromedriver finds `/usr/bin/chromium` directly without a wrapper detour.
  This eliminates a potential version-mismatch source for the crash.
- Add browser/driver discovery logging at startup so versions can be
  verified in the HA log.

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
