# Home Assistant Add-on: Grass Node

Run a [Grass](https://getgrass.io) node directly from Home Assistant and earn
points by sharing your unused internet bandwidth.

[![Add repository to my Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fssivtsov%2Fha-grass-addon)

## About

Grass is a network that pays you for your unused internet bandwidth. This
add-on runs the **official Grass desktop application** inside a noVNC session,
wrapping the community-maintained
[`mrcolorrain/grass-desktop`](https://hub.docker.com/r/mrcolorrain/grass-desktop)
image (from [MRColorR/get-grass](https://github.com/MRColorR/get-grass)) as a
native Home Assistant add-on:

- Runs the genuine Grass desktop app — it tries to log in automatically, and
  if that fails you log in **by hand** through the noVNC web UI.
- Built-in **noVNC web UI** (port `6080`) and **VNC** (port `5900`).
- **amd64 only** — the Grass desktop app is an x86 Electron app and does not
  run on ARM devices.

## Installation

1. In Home Assistant go to **Settings → Add-ons → Add-on Store**.
2. Open the **⋮** menu (top right) → **Repositories** and add:
   `https://github.com/ssivtsov/ha-grass-addon`
3. Find **Grass Node** in the store and click **Install**.
4. Open the **Configuration** tab and set your Grass account email and
   password (register at [app.getgrass.io](https://app.getgrass.io/register)
   if you don't have an account).
5. Start the add-on and open the **Web UI** (port `6080`). If auto-login
   didn't succeed, log in by hand in the Grass app window shown there.
6. Once connected, your device will show up on the
   [Grass dashboard](https://app.getgrass.io).

## Configuration

```yaml
user_email: you@example.com        # Grass account email (for auto-login)
user_password: your-password       # Grass account password (for auto-login)
try_autologin: true                # attempt auto-login; log in manually if it fails
vnc_password: change-me            # noVNC / VNC access password
vnc_resolution: 1280x720           # virtual screen resolution
```

See the add-on **Documentation** tab for the full option reference and
troubleshooting tips.

## Add-ons in this repository

| Add-on | Description |
| ------ | ----------- |
| [Grass Node](./grass_node) | Run a Grass (getgrass.io) node and earn points for shared bandwidth. |

## Disclaimer

This is an **unofficial** add-on, not affiliated with Grass / Wynd Network or
with the upstream image maintainers. Sharing bandwidth has inherent risks —
use at your own discretion.
