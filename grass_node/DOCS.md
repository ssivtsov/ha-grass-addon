# Grass Node Add-on

Run a [Grass](https://getgrass.io) node from Home Assistant and earn points by
sharing your unused internet bandwidth.

Since version 2.0.0 the add-on is built on top of the community-maintained
[`autonomylabxyz/grass`](https://hub.docker.com/r/autonomylabxyz/grass)
image (source: [autonomylab-xyz/grass](https://github.com/autonomylab-xyz/grass)).
It runs a headless Chromium with the official Grass extension, logs into your
Grass account automatically and keeps the connection alive. A small status
page shows the connection state, network quality and lifetime earnings.

## Prerequisites

You need a Grass account. If you don't have one yet, register at
[app.getgrass.io](https://app.getgrass.io/register).

## Configuration

| Option | Required | Description |
| ------ | -------- | ----------- |
| `user_email` | yes | The email of your Grass account. |
| `user_password` | yes | The password of your Grass account. |
| `allow_debug` | no | On login failure, capture a screenshot/browser log and upload them to a public image host for troubleshooting. Default: `false`. |

Example:

```yaml
user_email: you@example.com
user_password: your-grass-password
allow_debug: false
```

Options from 1.x (`vnc_password`, `vnc_resolution`, `headless`,
`max_retry_multiplier`) are deprecated and ignored — you can remove them from
your configuration.

## Web UI (status page)

After the add-on starts, open the Web UI from the add-on page (or navigate to
`http://<home-assistant-host>:8080`). It returns the current connection
status, network quality and earnings. There is no VNC interface anymore —
the browser always runs headless.

## Verifying it works

1. Check the add-on log — you should see the login being performed and the
   extension connecting.
2. Open the Web UI — it should report a connected status.
3. Open the [Grass dashboard](https://app.getgrass.io) — your device should
   appear as connected and start accumulating points.

## Notes & troubleshooting

- **Architectures:** `amd64` and `aarch64` are supported (separate upstream
  tags, selected automatically at build time).
- **One node per IP:** Grass rewards are typically limited per public IP.
  Running multiple nodes behind the same IP will not multiply earnings.
- **Resources:** headless Chromium typically uses a few hundred MB of RAM —
  noticeably less than the 1.x VNC-based image.
- **Login failures:** if the log shows a login error, verify the credentials,
  then optionally enable `allow_debug` to capture a screenshot of what the
  browser saw (note: the screenshot is uploaded to a public image host).
- This is an **unofficial** community add-on and is not affiliated with
  Grass / Wynd Network. Use at your own discretion.
