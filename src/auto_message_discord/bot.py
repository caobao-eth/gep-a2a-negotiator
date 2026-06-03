from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence

import discord

from .ai import chunk_discord_message, generate_ai_reply, should_ai_reply
from .config import BotConfig
from .messages import load_messages

logger = logging.getLogger(__name__)


class AutoMessageBot(discord.Client):
    def __init__(self, config: BotConfig):
        intents = discord.Intents.default()
        if config.ai.enabled:
            intents.message_content = True
        super().__init__(intents=intents)
        self.config = config
        self.messages: Sequence[str] = load_messages(config.messages_file)
        self._sent_count = 0

    async def on_ready(self) -> None:
        logger.info("Logged in as %s", self.user)
        if self.config.startup_message:
            logger.info(
                "Auto-message loop starting: channel=%s messages=%d dry_run=%s",
                self.config.channel_id,
                len(self.messages),
                self.config.dry_run,
            )
        self.loop.create_task(self._message_loop())

    async def on_message(self, message: discord.Message) -> None:
        if not self.config.ai.enabled or message.author.bot:
            return

        bot_user_id = self.user.id if self.user else None
        should_reply, prompt = should_ai_reply(message.content, bot_user_id=bot_user_id, settings=self.config.ai)
        if not should_reply:
            return

        async with message.channel.typing():
            try:
                reply = await asyncio.to_thread(generate_ai_reply, prompt, self.config.ai)
            except Exception as exc:  # pragma: no cover - protects live bot loop
                logger.exception("AI reply failed")
                reply = f"AI reply failed: `{exc}`"

        for chunk in chunk_discord_message(reply):
            await message.reply(chunk, mention_author=False)

    async def _message_loop(self) -> None:
        await self.wait_until_ready()
        channel = self.get_channel(self.config.channel_id)
        if channel is None:
            channel = await self.fetch_channel(self.config.channel_id)

        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            raise TypeError("Configured channel_id is not a text channel or thread")

        while not self.is_closed():
            for message in self.messages:
                if self.config.max_messages_per_run and self._sent_count >= self.config.max_messages_per_run:
                    logger.info("max_messages_per_run reached; closing bot")
                    await self.close()
                    return

                await self._send_one(channel, message)
                self._sent_count += 1
                await asyncio.sleep(self.config.send_interval_seconds)

            if not self.config.loop_messages:
                logger.info("loop_messages=false; closing bot")
                await self.close()
                return

    async def _send_one(self, channel: discord.TextChannel | discord.Thread, content: str) -> None:
        if self.config.dry_run:
            logger.info("DRY RUN: would send to %s: %s", channel.id, content)
            return

        logger.info("Sending message %d to channel %s", self._sent_count + 1, channel.id)
        sent = await channel.send(content)

        if self.config.delete_after_seconds is not None:
            await asyncio.sleep(self.config.delete_after_seconds)
            try:
                await sent.delete()
                logger.info("Deleted message %s", sent.id)
            except discord.HTTPException as exc:
                logger.warning("Could not delete message %s: %s", sent.id, exc)


def run_bot(config: BotConfig) -> None:
    bot = AutoMessageBot(config)
    bot.run(config.token)
