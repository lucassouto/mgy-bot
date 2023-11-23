import asyncio
import logging
import platform
import sys

import discord
from decouple import config
from dotenv import load_dotenv

from bot import MGYBot
from utils import __program__
from utils.cmdline import display_banner
from utils.pgdatabase import Postgres

load_dotenv(override=True)
log = logging.getLogger("main")

# Below cogs represents our folder our cogs are in.
INITIAL_EXTENSIONS = [
    "cogs.max",
    "cogs.music",
    "cogs.events",
    "cogs.level",
    "cogs.games",
    "cogs.mod",
]

bot = MGYBot(
    command_prefix=MGYBot.build_prefixes,
    case_insensitive=True,
    description="Max Gay Yeah!",
    intents=MGYBot.get_intents(),
    game_actions=[],
    pg=Postgres(),
)


@bot.event
async def on_ready():
    """https://discordpy.readthedocs.io/en/stable/api.html#discord.on_ready"""

    log.info(f"\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n")
    # Changes Playing Status. type=1(streaming) for a standard game you could remove type and url.
    await bot.change_presence(activity=discord.Game(name=config("BOT_IN_GAME"), type=1))
    log.info("Successfully logged in and booted...!")


# after using async_with
async def main():
    log.debug("##################### Iniciando %s #########################", __program__)

    display_banner()

    if platform.system() == "Darwin":
        # If you use macOS and want to use music module, you need to load the opus and have libopus.dylib in your path
        # Example:
        # os.environ["OPUS_LIB_PATH"] = "/opt/homebrew/opt/opus/lib/libopus.dylib"  # noqa: ERA001
        discord.opus.load_opus("libopus.dylib")

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

bot.run(config("BOT_TOKEN"), reconnect=True)
