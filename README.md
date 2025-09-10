<div align="center">
  <a href="https://github.com/filippofinke/BashNVR">
    <img width="200px" src="https://github.com/user-attachments/assets/2b68e61e-419e-4433-a825-f4b9305f381e">
  </a>
  <h3 align="center">Slack Status Automation</h3>
</div>

> Lightweight Python service to automatically update Slack status based on a schedule and configurable rules.

This project lets you define status messages, emojis, and schedule rules so a small scheduler updates your Slack presence automatically. It supports both a local Python setup and a Docker-based deployment.

## Features

- [x] Scheduled status updates using a configurable scheduler
- [x] Read configuration from `config.yaml` (example provided)
- [x] Slack integration using a token-based API client
- [x] Dockerfile and `docker-compose.yml` for containerized deployment
- [x] Small, easy-to-read codebase (single module + package)

## Quick Start

Prerequisites

- Python 3.10+ (recommended)
- `pip` for installing dependencies
- A Slack user token with `users.profile:write` scope

Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create configuration

1. Copy the example config:

```bash
cp config.example.yaml config.yaml
```

2. Edit `config.yaml` and set your Slack token and schedules. At minimum set `slack.token` and one `schedules` entry.

Run locally

```bash
# run the small app which starts the scheduler
python slack_status.py
```

The service will read `config.yaml` from the repository root by default.

## Configuration

Open `config.example.yaml` (renamed to `config.yaml`) to see available settings. Typical fields:

Example snippet

```yaml
slack_token: "your-slack-token-here"

intervals:
  - time: "12:00"
    presence: "away"
    status_text: "Out for the day"
    status_emoji: ":x:"

  - time: "07:30"
    presence: "auto"
    status_text: "Working"
    status_emoji: ":white_check_mark:"
```

Security note: Do not commit real tokens into git. Prefer environment variables or secrets.

## Docker

Build and run with Docker Compose

```bash
docker compose build
docker compose up -d
```

Environment variables

Set the token via environment variables or a mounted `config.yaml`. Example `docker-compose.yml` in this repo demonstrates usage.

## Troubleshooting

- Logs: If running with Docker Compose, use `docker compose logs -f`.
- Token errors: ensure the token has `users.profile:write` scope.
- Config load errors: ensure YAML indentation is correct and required fields exist.

## Author

👤 **Filippo Finke**

- Website: [https://filippofinke.ch](https://filippofinke.ch)
- Twitter: [@filippofinke](https://twitter.com/filippofinke)
- Github: [@filippofinke](https://github.com/filippofinke)
- LinkedIn: [@filippofinke](https://linkedin.com/in/filippofinke)
