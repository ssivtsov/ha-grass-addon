# Home Assistant Add-on: Grass Node

Run a [Grass](https://getgrass.io) node directly from Home Assistant and earn
points by sharing your unused internet bandwidth.

[![Add repository to my Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fssivtsov%2Fha-grass-addon)

## About

Grass is a network that pays you for your unused internet bandwidth. This
add-on wraps the community-maintained
[`mrcolorrain/grass-node`](https://hub.docker.com/r/mrcolorrain/grass-node)
Docker image (from [MRColorR/get-grass](https://github.com/MRColorR/get-grass))
so it runs as a native Home Assistant add-on:

- Automatic login to your Grass account (Selenium-driven Chromium with the
  official Grass browser extension).
- Built-in **noVNC web UI** (port `6080`) and **VNC** (port `5900`) so you can
  watch the browser session or log in manually if needed.
- Automatic reconnect / retry with exponential backoff.
- Multi-arch: `amd64` and `aarch64`.

## Installation

1. In Home Assistant go to **Settings → Add-ons → Add-on Store**.
2. Open the **⋮** menu (top right) → **Repositories** and add:
   `https://github.com/ssivtsov/ha-grass-addon`
3. Find **Grass Node** in the store and click **Install**.
4. Open the **Configuration** tab and set your Grass account email and
   password (register at [app.getgrass.io](https://app.getgrass.io/register)
   if you don't have an account).
5. Start the add-on and check the **Log** tab. Once connected, your device
   will show up on the [Grass dashboard](https://app.getgrass.io).

## Configuration

```yaml
user_email: you@example.com        # Grass account email (required)
user_password: your-password       # Grass account password (required)
vnc_password: change-me            # noVNC / VNC access password
vnc_resolution: 1280x720           # virtual screen resolution
headless: false                    # run browser without UI (saves RAM)
max_retry_multiplier: 3            # retry backoff multiplier (1-10)
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
