from pathlib import Path

from auto_message_discord.config import load_config


def test_load_config_prefers_environment_token(tmp_path: Path, monkeypatch) -> None:
    cfg = tmp_path / "config.yml"
    messages = tmp_path / "messages.txt"
    messages.write_text("hello\n", encoding="utf-8")
    cfg.write_text(
        "token: ${DISCORD_BOT_TOKEN}\n"
        "channel_id: 123456789012345678\n"
        "messages_file: messages.txt\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "token-from-env")

    loaded = load_config(cfg)

    assert loaded.token == "token-from-env"
    assert loaded.channel_id == 123456789012345678
    assert loaded.messages_file == messages
