from __future__ import annotations

from pathlib import Path


def load_messages(path: str | Path) -> list[str]:
    message_path = Path(path)
    if not message_path.exists():
        raise FileNotFoundError(f"Messages file not found: {message_path}")

    messages: list[str] = []
    for raw in message_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        messages.append(line)

    if not messages:
        raise ValueError(f"No messages found in {message_path}")
    return messages
