"""
    Bot MGY para discord, toca musica e zoa com o max
"""
import logging

import discord
from decouple import config
from discord import Message
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database import SessionLocal

load_dotenv(override=True)
log = logging.getLogger("bot")


class MGYBot(commands.Bot):
    @property
    def session(self) -> AsyncSession:
        return SessionLocal()

    @staticmethod
    def build_prefixes(client: commands.Bot, message: Message) -> list[str]:
        """Prepare prefixes for bot call with @mention"""

        prefixes = config("BOT_PREFIXES", cast=lambda v: [s for s in v.split(",")])

        # Allow users to @mention the bot instead of using a prefix when using a command. Also optional
        return commands.when_mentioned_or(*prefixes)(client, message)

    @staticmethod
    def get_intents() -> discord.Intents:
        intents = discord.Intents.default()
        intents.message_content = True

        return intents
