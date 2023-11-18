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
from utils.pgdatabase import Postgres

load_dotenv(override=True)
log = logging.getLogger("bot")


class MGYBot(commands.Bot):
    def __init__(
        self,
        game_actions: list,
        in_game: bool = False,
        total_messages: int = 0,
        bonus_xp: bool = False,
        postgres_instance: Postgres = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.actions = game_actions
        self.game = in_game
        self.total_messages = total_messages
        self.pg = postgres_instance
        self.bonus_xp = bonus_xp

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
