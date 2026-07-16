# Grass Node Add-on

Run a [Grass](https://getgrass.io) node from Home Assistant and earn points by
sharing your unused internet bandwidth.

The add-on is built on top of the community-maintained
[`mrcolorrain/grass-node`](https://hub.docker.com/r/mrcolorrain/grass-node)
image (source: [MRColorR/get-grass](https://github.com/MRColorR/get-grass)).
It starts a lightweight Chromium browser with the official Grass extension,
logs into your Grass account automatically and keeps the connection alive.
A VNC / noVNC interface is included so you can watch or control the browser.

## Prerequisites

You need a Grass account. If you don't have one yet, register at
[app.getgrass.io](https://app.getgrass.io/register).

## Configuration

| Option | Required | Description |
| ------ | -------- | ----------- |
| `user_email` | yes | The email of your Grass account. |
| `user_password` | yes | The password of your Grass account. |
| `vnc_password` | no | Password for the VNC / noVNC interface. Default: `money4band` (upstream image default). Change it! |
| `vnc_resolution` | no | Virtual screen resolution, e.g. `1280x720`. |
| `headless` | no | Run the browser in headless mode (lower resource usage, but the noVNC view will not show the browser). Default: `false`. |
| `max_retry_multiplier` | no | Multiplier for the exponential backoff used when login or extension checks fail (1–10). Default: `3`. |

Example:

```yaml
user_email: you@example.com
user_password: your-grass-password
vnc_password: change-me
vnc_resolution: 1280x720
headless: false
max_retry_multiplier: 3
```

## Web UI (noVNC)

After the add-on starts, open the Web UI (port `6080`) from the add-on page
or navigate to `http://<home-assistant-host>:6080`. Enter the VNC password to
see the browser session running the Grass extension. A classic VNC client can
also connect on port `5900`.

If automatic login fails (e.g. Grass shows a CAPTCHA or changed its login
page), you can complete the login manually through the noVNC interface.

## Verifying it works

1. Check the add-on log — you should see the extension being downloaded,
   the login being performed, and periodic "connected" status checks.
2. Open the [Grass dashboard](https://app.getgrass.io) — your device should
   appear as connected and start accumulating points.

## Notes & troubleshooting

- **Architectures:** `amd64` and `aarch64` are supported (multi-arch upstream
  image).
- **One node per IP:** Grass rewards are typically limited per public IP.
  Running multiple nodes behind the same IP will not multiply earnings.
- **Resources:** the add-on runs a Chromium instance; expect roughly
  0.5–1 GB of RAM usage. On low-memory boards enable `headless` mode.
- **Browser crashes:** if the log shows Chromium crashing on a low-memory
  device, try enabling `headless` and/or lowering `vnc_resolution`.
- This is an **unofficial** community add-on and is not affiliated with
  Grass / Wynd Network. Use at your own discretion.
