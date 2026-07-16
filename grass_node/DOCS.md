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

## Logging in

1. Start the add-on and open the **Web UI** (port `6080`) from the add-on
   page, or navigate to `http://<home-assistant-host>:6080/vnc.html`.
2. Enter the VNC password (`vnc_password`) to see the Grass desktop app.
3. If auto-login succeeded, you'll see the app already logged in. If not,
   log in manually in the app window (enter your credentials, solve any
   CAPTCHA). The session then persists across restarts.

## Verifying it works

1. In the noVNC view the Grass app should show your account **connected**.
2. Open the [Grass dashboard](https://app.getgrass.io) — your device should
   appear as connected and start accumulating points.

## Notes & troubleshooting

- **amd64 only** — see Prerequisites. On ARM the add-on will not be offered.
- **Auto-login fails?** That's expected if Grass shows a CAPTCHA. Just log in
  manually through noVNC once.
- **One node per IP:** Grass rewards are typically limited per public IP.
- **Security warning:** the add-on runs with `full_access` so the desktop app
  behaves like a plain `docker run`. HA flags this — it's expected.
- This is an **unofficial** community add-on, not affiliated with Grass /
  Wynd Network. Use at your own discretion.
