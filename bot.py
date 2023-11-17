"""
    Bot MGY para discord, toca musica e zoa com o max
"""
import asyncio
import logging
import sys

import discord
from decouple import config
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from database import SessionLocal
from utils import __program__, logger  # pylint: disable=unused-import # noqa: F401
from utils.cmdline import display_banner
from utils.pgdatabase import Postgres

load_dotenv(override=True)
log = logging.getLogger("main")


def get_prefix(client, message):
    """Prepara prefixos para chamada do bot"""

    prefixes = config("BOT_PREFIXES", cast=lambda v: [s for s in v.split(",")])

    # Allow users to @mention the bot instead of using a prefix when using a command. Also optional
    return commands.when_mentioned_or(*prefixes)(client, message)


# Below cogs represents our folder our cogs are in.
INITIAL_EXTENSIONS = [
    "cogs.max",
    "cogs.music",
    "cogs.events",
    "cogs.level",
    "cogs.games",
    "cogs.mod",
]

intents = discord.Intents.default()
intents.message_content = True


class MGYBot(commands.Bot):
    @property
    def session(self) -> AsyncSession:
        return SessionLocal()


bot = MGYBot(
    command_prefix=get_prefix,
    case_insensitive=True,
    description="Max Gay Yeah!",
    intents=intents,
)

bot.game = False  # Variavel para verificar se esta ingame
bot.acoes = []  # Acoes para jogo
bot.total_mensagem = 0
bot.pg = Postgres()  # Instancia unica do Postgres
bot.bonusXP = False


@bot.event
async def on_ready():
    """https://discordpy.readthedocs.io/en/stable/api.html#discord.on_ready"""

    log.info(f"\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n")
    # Changes Playing Status. type=1(streaming) for a standard game you could remove type and url.
    await bot.change_presence(activity=discord.Game(name=config("BOT_GAME"), type=1))
    log.info("Successfully logged in and booted...!")


# after using async_with
async def main():
    """Main"""

    log.debug("##################### Iniciando %s #########################", __program__)

    display_banner()

    for extension in INITIAL_EXTENSIONS:
        try:
            await bot.load_extension(extension)
        except Exception as e:  # pylint: disable=broad-exception-caught
            log.critical("Failed to load extensions {extensions}. %s", e, exc_info=True)
            sys.exit()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()

bot.run(config("TOKEN"), reconnect=True)
