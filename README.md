# Arpspoof-Docker

A small, self-hosted HTTP service that can cut off (and restore) internet access for
individual devices on your own local network. It wraps the classic `arpspoof` tool
(from `dsniff`) in a tiny Flask API and ships it as a Docker container, so you can
disconnect a device with a single HTTP request — handy for parental controls,
enforcing "screen-off" times, or network administration on a network you own.

> ⚠️ **Use only on networks you own or are authorized to administer.** ARP spoofing
> intercepts traffic on the local segment. Running it against devices or networks
> without permission is illegal in many jurisdictions. See [Security & legal](#security--legal-notes).

### [Extensive 'How-to' blog post](https://en.techblog.co.il/home-assistant-cut-internet-connection-using-arpspoof/)

---

## Table of contents

- [How it works](#how-it-works)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Docker Compose](#docker-compose)
  - [Docker run](#docker-run)
  - [Build from source](#build-from-source)
- [Configuration](#configuration)
- [Usage & API reference](#usage--api-reference)
- [Integrations](#integrations)
- [Security & legal notes](#security--legal-notes)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## How it works

The container runs a Flask web server (default port `7022`) that exposes a handful of
endpoints. When you ask it to disconnect a device by IP, it launches:

```
arpspoof -i <INTERFACE_NAME> -t <device_ip> <ROUTER_IP>
```

This tells the target device that the container is the router, so the device's traffic
is redirected to the container instead of the real gateway. Because the container does not forward that
traffic, the device effectively loses its internet connection. Reconnecting simply
kills the `arpspoof` process for that IP, and the device's ARP table recovers on its own.

Because ARP operates at layer 2, the container **must** share the same physical LAN
segment as the devices it manages, which is why it runs with host networking.

## Features

- Disconnect a single LAN device from the internet by IP address.
- Reconnect a previously disconnected device.
- Query whether a device is currently being spoofed (disconnected).
- Simple HTTP/REST interface — easy to call from scripts, cron, or Home Assistant.
- Multi-architecture Docker Hub images (`amd64`, `arm64`).

## Requirements

- A Linux Docker host on the **same layer-2 subnet** as the devices you want to manage.
- **Host networking** (`network_mode: host`) — as set in the provided
  [`docker-compose.yaml`](docker-compose.yaml). ARP spoofing does not work from a bridged
  container network.
- Permission to send raw ARP packets. `arpspoof` (from `dsniff`) needs raw-socket access;
  this is typically granted via the `NET_RAW` / `NET_ADMIN` capabilities.
  <!-- TODO: verify — the provided docker-compose.yaml sets only network_mode: host and does
  not declare cap_add: [NET_RAW, NET_ADMIN]. Confirm whether host networking alone is
  sufficient on your host or whether these capabilities must be added. -->
- The **router/gateway IP** and the host **interface name** (see [Configuration](#configuration)).

## Installation

### Docker Compose

```yaml
version: "3.7"

services:

  arpspoof:
    image: techblog/arpspoof-docker
 #   build: https://github.com/t0mer/Arpspoof-Docker.git
    network_mode: host #Network mode must be set to host
    container_name: arpspoof
    restart: unless-stopped
    labels:
      - "com.ouroboros.enable=true"
    environment:
      - ROUTER_IP= #Required Router IP
      - INTERFACE_NAME= #Required Interface name, can use this command to get it: ip route get 8.8.8.8 | sed -nr 's/.*dev ([^\ ]+).*/\1/p'
```

Then start it:

```bash
docker compose up -d
```

### Docker run

```bash
docker run -d \
  --name arpspoof \
  --network host \
  --restart unless-stopped \
  -e ROUTER_IP=192.168.1.1 \
  -e INTERFACE_NAME=eth0 \
  techblog/arpspoof-docker
```

A manual GitHub Actions workflow can also publish the image to the GitHub Container
Registry as `ghcr.io/t0mer/arpspoof-docker` (built for `amd64`, `arm64`, and `arm/v7`).

### Build from source

```bash
git clone https://github.com/t0mer/Arpspoof-Docker.git
cd Arpspoof-Docker
docker build -t arpspoof-docker .
```

## Configuration

All configuration is provided through environment variables. Both variables are
**required** and have no default — if they are unset they are read as `None`, and the
`/disconnect` and `/reconnect` calls will raise an error internally and return `0`.

| Variable         | Required | Default | Description |
|------------------|----------|---------|-------------|
| `ROUTER_IP`      | Yes      | _(none)_ | IP address of your router/gateway (the host that `arpspoof` impersonates). |
| `INTERFACE_NAME` | Yes      | _(none)_ | Name of the host network interface on the LAN, e.g. `eth0`. Find it with: `ip route get 8.8.8.8 \| sed -nr 's/.*dev ([^\ ]+).*/\1/p'` |

The service always listens on TCP port **7022**.

## Usage & API reference

The API takes the target device's IP as a query-string parameter (`ip`) and returns a
plain-text string (`"1"` / `"0"`). All endpoints use `GET`.

| Method | Path          | Query params | Purpose | Response |
|--------|---------------|--------------|---------|----------|
| GET    | `/`           | —            | Liveness check. | `Number five is alive!` |
| GET    | `/status`     | `ip`         | Check whether the device is currently disconnected (spoofed). | `1` = spoof process running (disconnected), `0` = not running. |
| GET    | `/disconnect` | `ip`         | Start ARP spoofing the device — blocks its internet access. | `1` on success, `0` on error. |
| GET    | `/reconnect`  | `ip`         | Stop spoofing the device — restores its internet access. | `1` on success, `0` on error. |

> Note: `/status` returns `1` (rather than `0`) if the status check itself raises an
> error, so treat a `1` from `/status` as "assume still disconnected".

### Examples

Assuming the service runs on `192.168.1.10:7022` and you want to manage the device
`192.168.1.50`:

```bash
# Health check
curl http://192.168.1.10:7022/

# Disconnect the device from the internet
curl "http://192.168.1.10:7022/disconnect?ip=192.168.1.50"

# Check its status (1 = disconnected, 0 = connected)
curl "http://192.168.1.10:7022/status?ip=192.168.1.50"

# Reconnect the device
curl "http://192.168.1.10:7022/reconnect?ip=192.168.1.50"
```

## Integrations

### Home Assistant

The service is designed to be driven from Home Assistant using `rest_command` /
`command_line` entities that call the `/disconnect`, `/reconnect`, and `/status`
endpoints — for example to build a switch that cuts a child's device off the internet.
The linked
[blog post](https://en.techblog.co.il/home-assistant-cut-internet-connection-using-arpspoof/)
walks through a full Home Assistant setup.

## Security & legal notes

- **No authentication.** The API has no authentication or authorization: anyone who can
  reach port `7022` can disconnect or reconnect any device by IP. Keep the service on a
  trusted network, do **not** expose port `7022` to the internet, and restrict access
  with your firewall.
- **Unvalidated input.** The `ip` request parameter is passed to a shell command without
  validation, so the API must only be reachable by trusted clients on a trusted network.
- **Only your own network.** ARP spoofing manipulates other devices' traffic on the
  local segment. Only run this against devices on a network you own or are explicitly
  authorized to administer.
- **Host networking + raw packets.** The container needs host networking and raw-socket
  access, which is a privileged posture — treat the host accordingly.

## Troubleshooting

- **A device is not disconnecting.** Confirm `ROUTER_IP` and `INTERFACE_NAME` are set
  correctly and that the container runs with `network_mode: host` on the same subnet as
  the target device. Re-check the interface name with the command in
  [Configuration](#configuration).
- **`arpspoof: couldn't arp for host` / permission errors.** The container may lack raw
  socket privileges; ensure it runs with host networking and, if needed, the
  `NET_RAW` / `NET_ADMIN` capabilities.
- **`/status` always returns `1`.** `/status` returns `1` both when the device is
  disconnected and when the internal status check errors — verify the IP is correct.

## Development

The application is a single Flask module, [`arpspoof/arpspoof.py`](arpspoof/arpspoof.py),
built on:

- **Flask** serves the routes (defined with plain `@app.route`). `flask-restful` is a
  dependency and an `Api(app)` is created, but it is currently unused (no `Resource` is
  registered).
- **loguru** for logging.
- **arpspoof** (from the `dsniff` package) for the actual ARP spoofing, installed in the
  [`Dockerfile`](Dockerfile) on top of the `techblog/flask` base image.

To iterate locally, edit the code under `arpspoof/`, rebuild the image
(`docker build -t arpspoof-docker .`), and run it as shown above. The version shipped in
image tags is read from the [`VERSION`](VERSION) file by the release workflow.

## Contributing

Issues and pull requests are welcome. Please open an issue to discuss significant
changes before submitting a PR.

## License

Licensed under the **Apache License 2.0**. See the [License](License) file for details.
