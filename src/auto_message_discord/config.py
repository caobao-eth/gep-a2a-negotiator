from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import os
import yaml


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

    return BotConfig(
        token=str(token),
        channel_id=int(channel_id),
        messages_file=messages_file,
        send_interval_seconds=int(data.get("send_interval_seconds", 60)),
        delete_after_seconds=(
            None if data.get("delete_after_seconds") in (None, "", False)
            else int(data.get("delete_after_seconds"))
        ),
        loop_messages=bool(data.get("loop_messages", True)),
        dry_run=bool(data.get("dry_run", False)),
        max_messages_per_run=(
            None if data.get("max_messages_per_run") in (None, "", 0)
            else int(data.get("max_messages_per_run"))
        ),
        startup_message=bool(data.get("startup_message", True)),
    )
