"""
    Modulo cuidar dos niveis dos usuarios
"""
import logging
import os
from datetime import UTC, datetime
from random import randint

import discord
from decouple import config
from discord.ext import commands
from discord.utils import get
from sqlalchemy import ScalarResult

from bot import MGYBot
from models import Level as LevelModel
from models import Server, User
from repositories import LevelRepository, ServerRepository, UserRepository
from repositories.user_servers import UserServerRepository

log = logging.getLogger("Level")
BASE = 10  # Toda mensagem ganha a xp base
MAX_RAND = 14  # Toda mensagem ganha aleatorio entre 1 e este valor
MAX_LEVEL = 51  # Nivel máximo
MULTIPLER = 1.1  # O quanto de XP a mais precisa em comparação ao lvl anterior


class LevelException(Exception):
    ...


class Level(commands.Cog, name="Level"):
    """
    Classe para cuidar dos eventos de level
    """

    def __init__(self, bot: MGYBot):
        self.bot = bot

    async def set_discord_role(self, role_name: str, discord_user: discord.Member, guild: discord.Guild):
        role = get(guild.roles, name=role_name)
        await discord_user.add_roles(role)

    async def update_discord_role(
        self, discord_user: discord.Member, guild: discord.Guild, current_level: LevelModel, next_level: LevelModel
    ):
        """Atualiza cargo"""
        current_role_name = current_level.name
        new_role_name = next_level.name
        if current_role_name != new_role_name:
            log.info(f"Atualizando cargo de: {current_role_name} para {new_role_name}")
            new_role = get(guild.roles, name=new_role_name)
            await discord_user.add_roles(new_role)

            current_role = get(guild.roles, name=current_role_name)
            await discord_user.remove_roles(current_role)

    async def prox_nivel(self, nivel_atual: int):
        """Verifica a quantidade de exp pro proximo nivel"""
        nivel = 1000
        total = 1000  # level 1
        for i in range(1, nivel_atual):
            nextl = nivel * MULTIPLER
            nextl = nextl - nivel
            nivel += nextl
            total += nivel

        return total

    async def update_experience(self, user: User):
        experience = int(BASE + randint(0, MAX_RAND + int(user.level_id * 0.5)))

        if self.bot.bonus_xp:
            experience *= 2

        async with self.bot.session as session:
            await UserRepository(session).update(pk=user.id, data={"experience": user.experience + experience})

    async def evolve_user(self, user: User, discord_user: discord.Member, guild: discord.Guild) -> tuple[bool, int]:
        experience_required = await self.prox_nivel(user.level.value)
        if user.experience >= experience_required and user.level.value < MAX_LEVEL:
            async with self.bot.session as session:
                current_level = user.level
                levels = await LevelRepository(session).filter(value=user.level.value + 1)
                next_level = levels.first()
                await UserRepository(session).update(pk=user.id, data={"level_id": next_level.id})
                await self.update_discord_role(
                    discord_user=discord_user, guild=guild, current_level=current_level, next_level=next_level
                )
                return True, next_level.value
        return False, user.level.value

    async def insert_user(self, guild: discord.Guild, author: discord.Member) -> User:
        log.info("Inserindo usuário")
        async with self.bot.session as session:
            servers: ScalarResult[Server] = await ServerRepository(session).filter(discord_id=str(guild.id))
            server = servers.first()

            if not server:
                error = f"Servidor {guild.name} não encontrado"
                log.error(error)
                raise LevelException(error)

            levels = await LevelRepository(session).filter(value=1)
            level = levels.first()
            if not level:
                error = "Level 1 não encontrado"
                log.error(error)
                raise LevelException(error)

            data = {
                "name": author.name,
                "discord_user_id": str(author.id),
                "level_id": level.id,
                "experience": 0,
                "total_messages": 0,
                "updated_at": datetime.now(UTC).replace(tzinfo=None),
            }
            user: User = await UserRepository(session).create(data=data)
            log.info(f"Usuário {user.name} adicionado!")

            await UserServerRepository(session).create(data={"user_id": user.id, "server_id": server.id})

            users: ScalarResult[User] = await UserRepository(session).filter(
                discord_user_id=str(author.id), load_relationship=True
            )
            user = users.first()
            await self.set_discord_role(role_name=user.level.name, discord_user=author, guild=guild)
            return user

    async def update_total_messages(self, message: discord.Message) -> None:
        """Soma 1 na quantidade de mensagens do usuario"""
        async with self.bot.session as session:
            users: ScalarResult[User] = await UserRepository(session).filter(
                discord_user_id=str(message.author.id), load_relationship=True
            )
            user = users.first()

            if not user:
                log.error("Usuário não encontrado")
                log.info("Inserindo usuário")
                user = await self.insert_user(guild=message.guild, author=message.author)

            await UserRepository(session).update(pk=user.id, data={"total_messages": user.total_messages + 1})

    async def update(self, message: discord.Message) -> tuple[bool, int]:
        """Atualiza"""
        async with self.bot.session as session:
            users: ScalarResult[User] = await UserRepository(session).filter(
                discord_user_id=str(message.author.id), load_relationship=True
            )
            user = users.first()

            if not user:
                log.error("Usuário não encontrado")
                log.info("Inserindo usuário")
                user = await self.insert_user(guild=message.guild, author=message.author)

            await self.update_experience(user=user)
            await session.refresh(user)
            evolved, level = await self.evolve_user(user=user, discord_user=message.author, guild=message.guild)
            return evolved, level

    @commands.command(aliases=["exp", "experiencia", "xp"])
    async def experience(self, ctx: commands.Context):
        """Mostra o nivel e experiencia atual"""

        def build_footer_infos(guild_id: int) -> tuple:
            icon_url = config("BOT_ICON")
            if guild_id in [470710752789921803, 582709300506656792]:
                text = {
                    470710752789921803: os.environ["MACRO"],
                    582709300506656792: os.environ["MACRO2"],
                }[guild_id]
                return text, icon_url
            return config("BOT_DESCRIPTION", default="MGY"), icon_url

        async with self.bot.session as session:
            users: ScalarResult[User] = await UserRepository(session).filter(
                discord_user_id=str(ctx.author.id), load_relationship=True
            )
            user = users.first()

        if not user:
            await ctx.send("Usuário não encontrado")
            return

        if str(ctx.guild.id) not in [server.discord_id for server in user.servers]:
            error = f"Usuário {user.name} não pertence a esse servidor"
            log.error(error)
            raise LevelException(error)

        log.info("Buscando exp do usuário")

        embed = discord.Embed(colour=0xFA00D4)
        embed.set_author(
            name=ctx.author.name,
            url="https://www.youtube.com/watch?v=Tu5-h4Ye0J0",
            icon_url=ctx.author.avatar.url,
        )
        embed.add_field(name="Level atual", value=f"{user.level.value} - {user.level.name}")
        embed.add_field(name="Exp atual", value=user.experience)
        embed.add_field(
            name="Próximo nível em",
            value=str(int((await self.prox_nivel(user.level.value)) - user.experience)),
        )

        text, icon_url = build_footer_infos(ctx.guild.id)
        embed.set_footer(text=text, icon_url=icon_url)

        await ctx.send(embed=embed)


async def setup(bot: MGYBot):
    """Adiciona cog ao bot"""
    await bot.add_cog(Level(bot))
