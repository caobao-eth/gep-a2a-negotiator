from auto_message_discord.ai import AISettings, chunk_discord_message, should_ai_reply


def test_should_reply_to_prefix() -> None:
    settings = AISettings(enabled=True, trigger_prefix="!ai")
    should, prompt = should_ai_reply("!ai help me", bot_user_id=123, settings=settings)

    assert should is True
    assert prompt == "help me"


def test_should_reply_to_mention() -> None:
    settings = AISettings(enabled=True, reply_when_mentioned=True)
    should, prompt = should_ai_reply("<@123> summarize this", bot_user_id=123, settings=settings)

    assert should is True
    assert prompt == "summarize this"


def test_should_not_reply_when_disabled() -> None:
    settings = AISettings(enabled=False)
    should, prompt = should_ai_reply("!ai help", bot_user_id=123, settings=settings)

    assert should is False
    assert prompt == ""


def test_chunk_discord_message() -> None:
    chunks = chunk_discord_message("a" * 4100, limit=1900)

    assert len(chunks) == 3
    assert all(len(chunk) <= 1900 for chunk in chunks)
