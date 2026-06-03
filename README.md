# Auto Message Discord

A safe, configurable Discord automation bot for scheduled announcements **and optional AI-powered community assistance**.

Auto Message Discord helps community maintainers rotate reminders, post announcements, and answer member questions through an optional OpenAI integration. It is designed as a small but production-minded open-source project: packaged Python code, CLI entrypoint, tests, CI, security guidance, and secret-safe configuration.

## Why this project matters

Discord communities often need repeated operational messages: rules, event reminders, onboarding tips, and support guidance. Many small bots hardcode secrets or encourage spammy behavior. This project provides a cleaner, maintainable alternative with dry-run testing, rate-conscious scheduling, and optional AI chat support for legitimate server maintainers.

## Features

### Scheduled messages

- Send messages from a plain text file
- Configurable interval between messages
- Optional message deletion after a delay
- Loop mode for recurring reminders
- Safety cap via `max_messages_per_run`
- Dry-run mode to validate messages before sending

### AI chat assistant

- Optional OpenAI integration
- Reply via command prefix, e.g. `!ai summarize the event plan`
- Reply when the bot is mentioned
- Configurable model and system prompt
- Discord-safe message chunking for long replies
- Environment-based API key handling

### Maintainer-friendly engineering

- Python package under `src/`
- CLI command: `auto-message-discord`
- YAML config example
- `.env.example` with no real secrets
- Tests with pytest
- GitHub Actions CI
- MIT license
- Security policy

## Use cases

- Community reminder rotation
- Event countdowns and schedule notices
- Server onboarding tips
- Moderator helper bot
- AI-assisted FAQ for community members
- Internal team notification loops

> Use responsibly. This project is intended for Discord servers you own or administer. Keep intervals respectful and follow Discord's Terms of Service.

## Quick start

### 1. Clone

```bash
git clone https://github.com/caobao-eth/Auto-Message-Discord.git
cd Auto-Message-Discord
```

### 2. Install

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .
```

For AI support:

```bash
pip install -e .[ai]
```

### 3. Configure

```bash
cp config.example.yml config.yml
cp .env.example .env
```

Set secrets as environment variables:

```bash
export DISCORD_BOT_TOKEN="your-discord-bot-token"
export DISCORD_CHANNEL_ID="123456789012345678"
export OPENAI_API_KEY="your-openai-api-key"  # only needed if ai.enabled=true
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

See [`config.example.yml`](config.example.yml).

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

ai:
  enabled: false
  model: "gpt-4o-mini"
  trigger_prefix: "!ai"
  reply_when_mentioned: true
  max_output_tokens: 350
  system_prompt: >
    You are a helpful Discord community assistant. Answer concisely,
    avoid spam, and help moderators and members understand schedules,
    announcements, and community information.
```

## AI assistant examples

Enable AI:

```yaml
ai:
  enabled: true
```

Then ask in Discord:

```text
!ai summarize this week's event schedule
```

Or mention the bot:

```text
@AutoMessageBot explain the server rules in simple terms
```

## Discord permissions

The bot needs:

- View Channel
- Send Messages
- Read Message History
- Manage Messages, only if `delete_after_seconds` is enabled

For AI replies, enable the Message Content Intent in the Discord Developer Portal.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[ai,dev]
pytest -q
python -m auto_message_discord.cli --config config.example.yml --dry-run
```

## Roadmap

- Per-channel schedules
- Cron-style schedule windows
- Admin-only commands
- Message template variables
- OpenAI-powered message drafting
- Moderation-aware pre-send checks
- Web dashboard for editing messages
- Docker image and compose file

## Security

Never commit real bot tokens or API keys. If a token is exposed, rotate it immediately in the Discord Developer Portal or OpenAI dashboard.

See [`SECURITY.md`](SECURITY.md).

## License

MIT — see [`LICENSE`](LICENSE).
