# Security Policy

## Supported versions

Security fixes are applied to the latest `main` branch.

## Reporting a vulnerability

Please open a private security advisory on GitHub or contact the maintainer directly.

Do not publish active bot tokens, server IDs, or private channel data in public issues.

## Secret handling

- Store Discord bot tokens in environment variables.
- Do not commit `.env` or real `config.yml` files.
- Rotate a token immediately if it is exposed.
- Grant the bot only the permissions it needs.
