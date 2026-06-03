from pathlib import Path

from auto_message_discord.messages import load_messages


def test_load_messages_ignores_blank_and_comments(tmp_path: Path) -> None:
    path = tmp_path / "messages.txt"
    path.write_text("hello\n\n# comment\nworld\n", encoding="utf-8")

    assert load_messages(path) == ["hello", "world"]
