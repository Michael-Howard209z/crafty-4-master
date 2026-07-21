<div align="center">
  <img src="app/frontend/static/assets/images/logo_long.svg" alt="Crafty Controller Logo" width="400"/>
  <h1>Crafty Controller 4</h1>
  <p><em>Python-based Minecraft Server Control Panel</em></p>

  [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
  [![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
  [![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20Docker-lightgrey)](https://craftycontrol.com)
  ![Maintenance](https://img.shields.io/badge/maintenance-active-green)
</div>

---

> **⚠️ Unofficial Modified Fork** — This is a fork of [Crafty Controller](https://gitlab.com/crafty-controller/crafty-4) with additional features and improvements. It is **not** the official project.

---

## 📋 Table of Contents

- [What is Crafty Controller?](#what-is-crafty-controller)
- [Disclaimer](#disclaimer)
- [Comparison with Official](#comparison-with-official)
- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
  - [Docker (Recommended)](#docker-recommended)
  - [Manual (Linux/Windows)](#manual-linuxwindows)
  - [Development Setup](#development-setup)
- [Upgrade Guide](#upgrade-guide)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [FAQ](#faq)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)
- [Acknowledgements](#acknowledgements)

---

## What is Crafty Controller?

Crafty Controller is a web-based Minecraft Server Control Panel / Launcher. It runs your Minecraft server in the background and provides a clean web interface for administrators to manage their servers, users, backups, and more.

**Supported Platforms:** Linux, Windows, Docker

---

## Disclaimer

This project is a **modified fork** of [Crafty Controller](https://gitlab.com/crafty-controller/crafty-4). It is maintained independently and is **not affiliated** with the official Crafty Controller team. All original code remains under the GNU GPL v3.0 license.

Changes made to this fork are clearly documented in the version history. The original project's copyright and license terms apply to all derivative work.

---

## Comparison with Official

| Feature | Official Crafty | This Fork |
|---|---|---|
| Server Management | ✅ | ✅ |
| Web Dashboard | ✅ | ✅ (Enhanced UI) |
| User Management | ✅ | ✅ |
| Backup System | ✅ | ✅ |
| Docker Support | ✅ | ✅ |
| **Mod/Plugin Browser** | ❌ | ✅ (Modrinth integration) |
| **User Self-Registration** | ❌ | ✅ (Configurable) |
| **Per-User RAM Limits** | ❌ | ✅ (4GB default for new users) |

---

## Features

### Core
- 🖥️ **Web-based control panel** — manage servers from any browser
- 🔐 **Multi-user support** with role-based permissions
- 🐳 **Docker-native** — runs securely as non-root
- 📦 **Cross-platform** — Linux, Windows, Docker
- ☁️ **Auto-backup** — scheduled backups with pruning
- 📊 **Performance monitoring** — CPU, RAM, disk usage
- 📜 **Live console** — real-time server terminal with WebSocket

### Fork Additions
- 🔍 **Mod/Plugin Browser** — search, browse, and install mods and plugins directly from [Modrinth](https://modrinth.com) via the web UI, with version selection
- 📝 **User Registration** — self-service account creation page (toggle via settings)
- ⚖️ **RAM Limits** — new registered users default to 4 GB RAM per server, configurable per user
- 🎨 **UI Refinements** — cleaner templates, improved responsiveness, updated layout

### Upstream
> Documentation: <https://docs.craftycontrol.com>

---

## Screenshots

<!-- Screenshots unavailable at this time. Replace these placeholders with actual images. -->

| Dashboard | Server Management |
|---|---|
| `[Dashboard screenshot]` | `[Server detail screenshot]` |

| Mod/Plugin Browser | Registration Page |
|---|---|
| `[Modrinth browser screenshot]` | `[Registration form screenshot]` |

---

## Installation

### Docker (Recommended)

```yml
services:
  crafty:
    container_name: crafty_container
    image: registry.gitlab.com/crafty-controller/crafty-4:latest
    restart: always
    environment:
      - TZ=Etc/UTC
    ports:
      - "8000:8000"    # HTTP
      - "8443:8443"    # HTTPS
      - "8123:8123"    # DYNMAP
      - "19132:19132/udp" # BEDROCK
      - "25500-25600:25500-25600" # MC SERVER PORT RANGE
    volumes:
      - ./docker/backups:/crafty/backups
      - ./docker/logs:/crafty/logs
      - ./docker/servers:/crafty/servers
      - ./docker/config:/crafty/app/config
      - ./docker/import:/crafty/import
```

```sh
docker compose up -d
```

> **Warning:** Docker under WSL2 / Windows 11 / Docker Desktop has known issues with Minecraft server world corruption on stop/restart. Linux hosts are strongly recommended for production use.

<details>
<summary><b>Docker Run</b></summary>

```sh
docker run \
  --name crafty_container \
  --detach \
  --restart always \
  -p 25500-25600:25500-25600 \
  -p 8000:8000 \
  -p 8443:8443 \
  -e TZ=Etc/UTC \
  -v "$(pwd)/docker/backups:/crafty/backups" \
  -v "$(pwd)/docker/logs:/crafty/logs" \
  -v "$(pwd)/docker/servers:/crafty/servers" \
  -v "$(pwd)/docker/config:/crafty/app/config" \
  -v "$(pwd)/docker/import:/crafty/import" \
  registry.gitlab.com/crafty-controller/crafty-4:latest
```
</details>

<details>
<summary><b>Build from Source (Docker)</b></summary>

```sh
git clone https://gitlab.com/crafty-controller/crafty-4.git
cd crafty-4
docker build . -t crafty
docker compose -f docker/docker-compose.yml up -d
```
</details>

### Manual (Linux/Windows)

<details>
<summary><b>Prerequisites</b></summary>

- Python 3.11+
- Git
- A SQLite-backed filesystem (default)

</details>

<details>
<summary><b>Setup Steps</b></summary>

```sh
# Clone the repository
git clone https://gitlab.com/crafty-controller/crafty-4.git
cd crafty-4

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run Crafty
python main.py
```

Navigate to `https://localhost:8443` and complete the initial setup wizard.
</details>

### Development Setup

```sh
git clone https://gitlab.com/crafty-controller/crafty-4.git
cd crafty-4
python3 -m venv .venv 
source .venv/bin/activate
pip install -r requirements.txt
pip install black  # Code formatter
python main.py --dev
```

- Format code with `black` before committing
- The application auto-reloads in dev mode

---

## Upgrade Guide

### Docker

```sh
docker compose pull
docker compose up -d
```

### Manual

```sh
git pull origin master
source .venv/bin/activate
pip install -r requirements.txt --upgrade
# Review config_examples/ for any new settings
python main.py
```

> **Note:** Database migrations run automatically on startup.

---

## Project Structure

```
crafty-4/
├── app/
│   ├── classes/
│   │   ├── controllers/    # Business logic controllers
│   │   ├── helpers/        # Utility functions & config
│   │   ├── models/         # Database models (Peewee ORM)
│   │   └── web/
│   │       ├── routes/     # API & page route handlers
│   │       └── templates/  # Jinja2 HTML templates
│   ├── config/             # Runtime configuration
│   ├── frontend/
│   │   └── static/         # CSS, JS, images, fonts
│   ├── migrations/         # Database migrations
│   └── translations/       # i18n language files
├── backups/                # Server backups
├── servers/                # Server data directory
├── logs/                   # Application logs
├── import/                 # World import directory
├── docker/                 # Docker config & compose files
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
└── Dockerfile              # Docker build definition
```

---

## Configuration

Settings are managed through the web interface at **Settings → Config**.

<details>
<summary><b>Key Settings</b></summary>

| Setting | Type | Default | Description |
|---|---|---|---|
| `allow_registration` | Boolean | `False` | Enable user self-registration page |
| `language` | String | `en_EN` | Default language |
| `cookie_expire` | Integer | — | Session cookie lifetime |
| `max_login_attempts` | Integer | — | Login lockout threshold |
| `enable_user_self_delete` | Boolean | `False` | Allow users to delete own accounts |

Full configuration reference is available in `config_examples/`.
</details>

---

## FAQ

<details>
<summary><b>How do I enable user registration?</b></summary>

Go to **Settings → Config → Security** and set `allow_registration` to `true`. A "Register" link will appear on the login page.
</details>

<details>
<summary><b>How do I change the RAM limit for a user?</b></summary>

Admin users can set `max_ram_gb` when creating or editing a user via the admin panel. New registered users default to 4 GB.
</details>

<details>
<summary><b>Where can I get help?</b></summary>

- Official docs: <https://docs.craftycontrol.com>
- Official Discord: <https://discord.gg/9VJPhCE>
</details>

<details>
<summary><b>Can I contribute to this fork?</b></summary>

See [Contributing](#contributing) below. Pull requests are welcome!
</details>

---

## Roadmap

- [x] Mod/Plugin browser with Modrinth integration
- [x] User self-registration
- [x] Per-user RAM limits
- [ ] Server auto‑update configuration via Modrinth
- [ ] Registration CAPTCHA / rate limiting
- [ ] Modpack installation support
- [ ] Configurable default RAM limit setting

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for the official guide.

1. Fork the repository
2. Create a branch from `dev` (`feature/`, `bugfix/`, `tweak/`, `lang/`)
3. Format code with [Black](https://black.readthedocs.io)
4. Test your changes
5. Submit a merge request

---

## License

This project is licensed under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) for the full text.

```
Crafty 4
Copyright (C) 2022  Crafty Controller

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
```

---

## Credits

### Original Project

**[Crafty Controller](https://gitlab.com/crafty-controller/crafty-4)** — The original Crafty Controller team for creating and maintaining this incredible project.

- Project Homepage: <https://craftycontrol.com>
- Git Repository: <https://gitlab.com/crafty-controller/crafty-4>
- Docker Hub: [`arcadiatechnology/crafty-4`](https://hub.docker.com/r/arcadiatechnology/crafty-4)
- Discord: <https://discord.gg/9VJPhCE>
- Documentation: <https://docs.craftycontrol.com>

### This Fork

Maintained independently as a fork with additional features. All modifications are released under the same GPL v3.0 license.

---

## Acknowledgements

- The [Modrinth](https://modrinth.com) team for their excellent API
- All Crafty Controller contributors and community members
- The open-source Python ecosystem (Tornado, Peewee, Jinja2, and more)

---

<div align="center">
  <sub>Built with NguyenHoang for the Minecraft server community</sub>
  <br>
  <sub>Not affiliated with Crafty Controller or Modrinth</sub>
</div>
