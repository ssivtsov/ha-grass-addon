# Grass Node Add-on

Run a [Grass](https://getgrass.io) node from Home Assistant and earn points by
sharing your unused internet bandwidth.

Since version 2.1.0 the add-on runs the **official Grass desktop application**
inside a noVNC session, using the community-maintained
[`mrcolorrain/grass-desktop`](https://hub.docker.com/r/mrcolorrain/grass-desktop)
image (source: [MRColorR/get-grass](https://github.com/MRColorR/get-grass)).

## Why the desktop app?

Earlier versions logged into `app.getgrass.io` by automating a headless
browser. Grass has since hardened its login page against automated logins,
so every browser-automation image now fails at the "loading login form" step.
Running the genuine desktop app avoids that: it tries to log in for you, and
if that fails you can log in **by hand** through the noVNC web UI. Once you're
logged in, the session persists.

## Prerequisites

- A Grass account — register at
  [app.getgrass.io](https://app.getgrass.io/register) if you don't have one.
- An **amd64 / x86-64** Home Assistant host. The Grass desktop app is an x86
  Electron application and does not run on ARM devices (Raspberry Pi, etc.).

## Configuration

| Option | Required | Description |
| ------ | -------- | ----------- |
| `user_email` | no | Grass account email, used for auto-login. Leave blank to log in entirely by hand. |
| `user_password` | no | Grass account password, used for auto-login. |
| `try_autologin` | no | Attempt automatic login with the email/password above. Default: `true`. |
| `password_link_tabs` | no | Advanced: Tab presses used during auto-login to reach "Use Password Instead". Default: `7`. |
| `vnc_password` | no | Password for the noVNC / VNC interface. Default: `money4band`. |
| `vnc_resolution` | no | Virtual screen resolution, e.g. `1280x720`. |

Example:

```yaml
user_email: you@example.com
user_password: your-grass-password
try_autologin: true
vnc_password: change-me
vnc_resolution: 1280x720
```

## Auto-login

With `user_email`, `user_password` and `try_autologin: true` (the default),
the add-on drives Grass's login for you: it types your email, presses
**Continue**, clicks **Use Password Instead**, types your password and presses
**Sign In**. A successful login is saved to `/data`, so it only happens once —
subsequent starts skip straight past the login.

### Tuning the click positions

Auto-login clicks the fields and buttons at fixed screen positions (offsets
from the Grass window's top-left corner, for the default 1280x720 screen):

- `email_xy` — email field (default `175,225`)
- `continue_xy` — CONTINUE button (default `175,296`)
- `use_password_xy` — "Use Password Instead" link (default `175,440`)
- `password_xy` — password field (default `175,225`)
- `signin_xy` — SIGN IN button (default `175,296`)

If a click misses, turn on `debug_screenshots`, look at where each step landed
in `/share/grass-debug/`, and correct the relevant `x,y` value. No rebuild
needed — just restart the add-on.

### Seeing what auto-login did (debug screenshots)

Set `debug_screenshots: true` to save a screenshot of each login step to
`/share/grass-debug/`:

- `grass-step1-email-typed.png`
- `grass-step2-after-continue.png`
- `grass-step3-after-use-password.png`
- `grass-step4-password-typed.png`
- `grass-step5-after-signin.png`

Browse `/share/grass-debug/` with the **File editor**, **Studio Code Server**
or **Samba** add-on. Turn the option off again once you're done — the shots
can contain the login page. (If `/share` isn't available they fall back to the
add-on's `/data`.)

## Manual login (fallback)

If auto-login misfires, log in by hand — you only need to do it once (the
session persists):

1. Open the **Web UI** (port `6080`), or `http://<home-assistant-host>:6080/vnc.html`.
2. Enter the VNC password (`vnc_password`) to see the Grass desktop app.
3. In the **Sign In** panel: type your **email** → **CONTINUE** → enter the
   emailed 6-digit code, or click **Use Password Instead** and type your
   password → **SIGN IN**.

## Verifying it works

1. In the noVNC view the Grass app should show your account **connected**.
2. Open the [Grass dashboard](https://app.getgrass.io) — your device should
   appear as connected and start accumulating points.

## Notes & troubleshooting

- **amd64 only** — see Prerequisites. On ARM the add-on will not be offered.
- **Auto-login fails?** That's expected — it's off by default. Just log in
  manually through noVNC once; the session is saved to `/data`.
- **Login lost after a restart?** The profile is persisted under
  `/data/app-config`. If you removed the add-on (not just restarted it) that
  data is deleted and you'll need to log in again.
- **One node per IP:** Grass rewards are typically limited per public IP.
- **Security warning:** the add-on runs with `full_access` so the desktop app
  behaves like a plain `docker run`. HA flags this — it's expected.
- This is an **unofficial** community add-on, not affiliated with Grass /
  Wynd Network. Use at your own discretion.
