# Security Policy

## Supported versions

Security fixes are applied to the latest `main` branch.

## Reporting a vulnerability

Please open a private security advisory on GitHub or contact the maintainer directly.

Do not publish active bot tokens, server IDs, or private channel data in public issues.

## Secret handling

- Store Discord bot tokens and OpenAI API keys in environment variables.
- Do not commit `.env` or real `config.yml` files.
- Rotate a token/key immediately if it is exposed.
- Grant the Discord bot only the permissions it needs.
- Use low default AI output limits to avoid runaway cost.
