# Auto Message Discord

A small, safe, open-source Discord bot for scheduled channel announcements, rotating reminders, and community operations.

The project is designed for maintainers who need a simple automation tool without hardcoding secrets or writing custom Discord API code.

## Highlights

- Scheduled Discord channel messages from a plain text file
- Optional message deletion after a configurable delay
- Loop mode for recurring announcements
- Dry-run mode for testing without sending messages
- YAML configuration with environment-variable token handling
- Minimal Python package with CLI entrypoint
- Security-conscious defaults: no tokens in git, `.env.example`, and clear setup docs

## Use cases

- Community reminder rotation
- Event countdown or schedule notices
- Server onboarding tips
- Temporary campaign announcements
- Internal team notification loops

> Use responsibly. This project is intended for servers you own or administer. Keep intervals respectful and follow Discord's Terms of Service.

## Quick start

### 1. Clone

```bash
git clone https://github.com/caobao-eth/Auto-Message-Discord.git
cd Auto-Message-Discord
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .
```

### 3. Configure

```bash
cp config.example.yml config.yml
cp .env.example .env
```

Set your token as an environment variable instead of putting it in Git:

```bash
export DISCORD_BOT_TOKEN="your-bot-token"
export DISCORD_CHANNEL_ID="123456789012345678"
```

Edit `messages.txt` with one message per line.

### 4. Test without sending

```bash
auto-message-discord --config config.yml --dry-run
```

### 5. Run

```bash
auto-message-discord --config config.yml
```

## Configuration

See [`config.example.yml`](config.example.yml):

```yaml
token: "${DISCORD_BOT_TOKEN}"
channel_id: "123456789012345678"
messages_file: "messages.txt"
send_interval_seconds: 60
delete_after_seconds: null
loop_messages: true
dry_run: false
max_messages_per_run: null
startup_message: true
```

## Message file format

`messages.txt`:

```text
Welcome to the server.
Remember to read the rules.
Weekly event starts at 20:00 UTC.
```

Blank lines and lines beginning with `#` are ignored.

## Discord permissions

Your bot needs:

- View Channel
- Send Messages
- Manage Messages, only if `delete_after_seconds` is enabled

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest
pytest
python -m auto_message_discord.cli --config config.example.yml --dry-run
```

## Roadmap

- Web dashboard for editing messages
- Per-channel schedules
- Cron-style schedule windows
- Import/export message packs
- Optional moderation-safe rate-limit presets
- Docker image and compose file

## Security

Never commit real bot tokens. If a token is exposed, rotate it immediately in the Discord Developer Portal.

See [`SECURITY.md`](SECURITY.md).

## License

MIT — see [`LICENSE`](LICENSE).
