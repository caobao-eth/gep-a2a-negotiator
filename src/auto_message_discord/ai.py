from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AISettings:
    enabled: bool = False
    model: str = "gpt-4o-mini"
    system_prompt: str = "You are a helpful Discord community assistant. Be concise, friendly, and safe."
    max_output_tokens: int = 350
    trigger_prefix: str = "!ai"
    reply_when_mentioned: bool = True


def should_ai_reply(content: str, *, bot_user_id: int | None, settings: AISettings) -> tuple[bool, str]:
    """Return whether the bot should answer and the cleaned prompt."""
    text = content.strip()
    if not settings.enabled:
        return False, ""

    if settings.trigger_prefix and text.startswith(settings.trigger_prefix):
        return True, text[len(settings.trigger_prefix):].strip()

    if settings.reply_when_mentioned and bot_user_id is not None:
        mention_variants = [f"<@{bot_user_id}>", f"<@!{bot_user_id}>"]
        for mention in mention_variants:
            if mention in text:
                return True, text.replace(mention, "").strip()

    return False, ""


def generate_ai_reply(prompt: str, settings: AISettings) -> str:
    if not prompt:
        return "Ask me something after the command, for example: `!ai summarize today's event plan`."

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OpenAI is enabled, but `OPENAI_API_KEY` is not configured."

    try:
        from openai import OpenAI
    except ImportError:
        return "OpenAI support requires the `openai` Python package. Install with `pip install -e .[ai]`."

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=settings.model,
        input=[
            {"role": "system", "content": settings.system_prompt},
            {"role": "user", "content": prompt},
        ],
        max_output_tokens=settings.max_output_tokens,
    )
    output = getattr(response, "output_text", "") or ""
    return output.strip() or "I could not generate a response."


def chunk_discord_message(text: str, limit: int = 1900) -> list[str]:
    text = text.strip()
    if not text:
        return [""]
    chunks: list[str] = []
    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)
        if split_at < 500:
            split_at = limit
        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()
    chunks.append(text)
    return chunks
