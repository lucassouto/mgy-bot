"""
    Modulo cuidar dos eventos on_SOMETHING
"""
import io
import logging
from datetime import UTC, datetime
from random import randint

import aiohttp
import discord
from decouple import config
from discord.ext import commands

from bot import MGYBot
from cogs.level import Level

log = logging.getLogger("Eventos")


class Event(commands.Cog, name="Eventos"):
    """
    Classe para cuidar dos eventos on_SOMETHING
    """

    def __init__(self, bot: MGYBot):
        self.bot = bot
        self.level = Level(bot)
        self.counter_remember = 0
        self.counter_frota = 0
        self.kick_list = [229043445010923520]  # TODO - add to kick list
        self.delay_seconds = config("DELAY_SECONDS", cast=int, default=45)
        self.delay_register = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Método que trata cada mensagem enviada"""
        log.info(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")

        channel = await self._get_channel(message=message)

        if message.author.bot:
            return

        await self.level.update_total_messages(message)
        if await self._verify_delay(author_id=message.author.id):
            evolved, level = await self.level.update(message)
            if evolved:
                await channel.send(f"Finalmente {message.author.mention} upou para o nível {level}! Glória a Deuxxx")

        await self._verify_max_message(message=message, channel=channel)
        await self._kick_user(message=message)
        await self._purge_messages(message=message)
        await self._happy_new_year(message=message)
        await self._verify_in_game(message=message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Método que trata erros"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Não entendi o que você quis dizer 😢")
            await ctx.send("https://media.giphy.com/media/SAAMcPRfQpgyI/giphy.gif")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)
        else:
            await ctx.send("Algo deu errado chame o admin!")
            await ctx.send("https://media.giphy.com/media/SFkjp1R8iRIWc/giphy.gif")

    async def _verify_delay(self, author_id: int) -> bool:
        """Implementa delay entre ganhos de xp"""
        now = datetime.now(UTC)
        timestamp: datetime = self.delay_register.get(author_id, None)
        if timestamp is None:
            self.delay_register[author_id] = now
            return True

        diff = now - timestamp
        if diff.seconds > self.delay_seconds:
            self.delay_register[author_id] = now
            return True

        return False

    async def _verify_max_message(self, message: discord.Message, channel: discord.TextChannel):
        if message.author.id != 229043445010923520:
            return

        await message.add_reaction("<:mgy:651473587022331928>")
        self.counter_remember += 1
        self.counter_frota += 1

        if self.counter_remember >= 14 and randint(1, 100) <= 24:
            await channel.send("Só estou passando aqui para lembrar a todos que o Max é gay.")
            self.counter_remember = 0
        else:
            log.info("counterLembra: %s", str(self.counter_remember))

        if self.counter_frota >= 20 and randint(1, 100) <= 24:
            self.counter_frota = 0

            async with aiohttp.ClientSession() as session, session.get("https://i.imgur.com/dvWqqcz.png") as resp:
                if resp.status != 200:
                    log.error("Deu ruim ao carregar imagem")
                    return
                data = io.BytesIO(await resp.read())
            await channel.send(file=discord.File(data, "cool_image.png"))
        else:
            log.info("counterFrota: %s", self.counter_frota)

    async def _kick_user(self, message: discord.Message):
        """
        1% de chance de kickar o usuário do canal de voz e excluir sua msg
        """

        if message.author.id in self.kick_list and randint(1, 200) <= 1:
            try:
                log.info(f"Kickando usuário {message.author.name}")
                pending_command = self.bot.get_command("move")
                ctx = await self.bot.get_context(message)
                await ctx.invoke(pending_command, message.author.id, "vaza")
            except Exception:
                log.exception("Erro ao kickar user")

    async def _purge_messages(self, message: discord.Message):
        if message.content == "mgy":
            await message.channel.purge(limit=1)
            await message.channel.send("Max Gay Yeah!")

        if message.content == "lenny":
            await message.channel.purge(limit=1)
            await message.channel.send("( ͡° ͜ʖ ͡°)")

    async def _happy_new_year(self, message: discord.Message):
        # TODO - automatizar mensagem no ano novo. Também automatizar mensagens customizadas em dias de aniversario, etc...
        if message.content == "novo":
            await message.channel.purge(limit=1)
            await message.channel.send(
                "Só estou passando aqui pra desejar um feliz ano novo! "
                "E lembrar o que o Max Gay. Bittenca Viadin. Jonas Líder. 24 Deus. Isaac Best Game."
            )

    async def _verify_in_game(self, message: discord.Message):
        if not self.bot.game:
            return

        self.bot.total_messages += 1
        try:
            action = int(message.content)
            self.bot.actions.append(action)
        except ValueError:
            pass

    async def _get_channel(self, message: discord.Message):
        if message.guild.id == 470710752789921803:
            return self.bot.get_channel(470740628213465114)  # Staff random shit
        return self.bot.get_channel(message.channel.id)


async def setup(bot: MGYBot):
    """Adiciona cog ao bot"""
    await bot.add_cog(Event(bot))
