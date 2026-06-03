from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import os
import yaml

from .ai import AISettings


@dataclass(frozen=True)
class BotConfig:
    token: str
    channel_id: int
    messages_file: Path
    send_interval_seconds: int = 60
    delete_after_seconds: int | None = None
    loop_messages: bool = True
    dry_run: bool = False
    max_messages_per_run: int | None = None
    startup_message: bool = True
    ai: AISettings = AISettings()


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    data = yaml.safe_load(path.read_text()) or {}
    if not isinstance(data, dict):
        raise ValueError("Config must be a YAML object")
    return data


def load_config(path: str | Path) -> BotConfig:
    config_path = Path(path)
    data = _read_yaml(config_path)

    token = os.getenv("DISCORD_BOT_TOKEN") or data.get("token")
    if token == "${DISCORD_BOT_TOKEN}":
        token = os.getenv("DISCORD_BOT_TOKEN")
    if not token or str(token).startswith(("your-", "replace-")):
        raise ValueError("Discord bot token is missing. Prefer DISCORD_BOT_TOKEN env var.")

    channel_id = os.getenv("DISCORD_CHANNEL_ID") or data.get("channel_id")
    if not channel_id or str(channel_id).startswith("your-"):
        raise ValueError("channel_id is missing")

    messages_file = Path(data.get("messages_file", "messages.txt"))
    if not messages_file.is_absolute():
        messages_file = config_path.parent / messages_file

    ai_data = data.get("ai") or {}
    if not isinstance(ai_data, dict):
        raise ValueError("ai config must be a YAML object")

    delete_after = data.get("delete_after_seconds")
    max_messages = data.get("max_messages_per_run")

    return BotConfig(
        token=str(token),
        channel_id=int(channel_id),
        messages_file=messages_file,
        send_interval_seconds=int(data.get("send_interval_seconds", 60)),
        delete_after_seconds=None if delete_after in (None, "", False) else int(delete_after),
        loop_messages=bool(data.get("loop_messages", True)),
        dry_run=bool(data.get("dry_run", False)),
        max_messages_per_run=None if max_messages in (None, "", 0) else int(max_messages),
        startup_message=bool(data.get("startup_message", True)),
        ai=AISettings(
            enabled=bool(ai_data.get("enabled", False)),
            model=str(ai_data.get("model", "gpt-4o-mini")),
            system_prompt=str(ai_data.get("system_prompt", AISettings().system_prompt)),
            max_output_tokens=int(ai_data.get("max_output_tokens", 350)),
            trigger_prefix=str(ai_data.get("trigger_prefix", "!ai")),
            reply_when_mentioned=bool(ai_data.get("reply_when_mentioned", True)),
        ),
    )
