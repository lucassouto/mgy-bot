"""
    Modulo cuidar dos niveis dos usuarios
"""
import os
import logging
from datetime import datetime

import discord
from random import randint

from discord.ext import commands
from discord.utils import get
from sqlalchemy import ScalarResult

from models import User, Server
from utils.pgdatabase import Postgres
from repositories import UserRepository, ServerRepository

log = logging.getLogger("Level")
BASE = 10  # Toda mensagem ganha a xp base
MAX_RAND = 14  # Toda mensagem ganha aleatorio entre 1 e este valor
MAX_LEVEL = 51  # Nivel máximo
MULTIPLER = 1.1  # O quanto de XP a mais precisa em comparação ao lvl anterior


def switchGuild(guild_id: int):
    """Switch case para pegar macro"""
    print(guild_id)
    return {
        470710752789921803: os.environ["MACRO"],
        582709300506656792: os.environ["MACRO2"],
    }.get(guild_id, "MGY")


def switch(x):
    """Switch case para pegar o novo cargo"""
    return {
        "0": "sem role",
        "1": "Rookies (lvl 1 - 5)",
        "2": "Rookies (lvl 1 - 5)",
        "3": "Rookies (lvl 1 - 5)",
        "4": "Rookies (lvl 1 - 5)",
        "5": "Rookies (Lvl 1 - 5)",
        "6": "Adventurers (lvl 6 - 10)",
        "7": "Adventurers (lvl 6 - 10)",
        "8": "Adventurers (lvl 6 - 10)",
        "9": "Adventurers (lvl 6 - 10)",
        "10": "Adventurers (lvl 6 - 10)",
        "11": "Veterans (lvl 11 - 15)",
        "12": "Veterans (lvl 11 - 15)",
        "13": "Veterans (lvl 11 - 15)",
        "14": "Veterans (lvl 11 - 15)",
        "15": "Veterans (lvl 11 - 15)",
        "16": "Monarchs (Lvl 16 - 20)",
        "17": "Monarchs (Lvl 16 - 20)",
        "18": "Monarchs (Lvl 16 - 20)",
        "19": "Monarchs (Lvl 16 - 20)",
        "20": "Monarchs (Lvl 16 - 20)",
        "21": "Kings (Lvl 21 - 25)",
        "22": "Kings (Lvl 21 - 25)",
        "23": "Kings (Lvl 21 - 25)",
        "24": "Kings (Lvl 21 - 25)",
        "25": "Kings (Lvl 21 - 25)",
        "26": "Emperors (Lvl 26 - 30)",
        "27": "Emperors (Lvl 26 - 30)",
        "28": "Emperors (Lvl 26 - 30)",
        "29": "Emperors (Lvl 26 - 30)",
        "30": "Emperors (Lvl 26 - 30)",
        "31": "The Living Legends (Lvl 31 - 35)",
        "32": "The Living Legends (Lvl 31 - 35)",
        "33": "The Living Legends (Lvl 31 - 35)",
        "34": "The Living Legends (Lvl 31 - 35)",
        "35": "The Living Legends (Lvl 31 - 35)",
        "36": "The Ascended Ones (Lvl 36 - 40)",
        "37": "The Ascended Ones (Lvl 36 - 40)",
        "38": "The Ascended Ones (Lvl 36 - 40)",
        "39": "The Ascended Ones (Lvl 36 - 40)",
        "40": "The Ascended Ones (Lvl 36 - 40)",
        "41": "Lesser Gods (Lvl 41 - 45)",
        "42": "Lesser Gods (Lvl 41 - 45)",
        "43": "Lesser Gods (Lvl 41 - 45)",
        "44": "Lesser Gods (Lvl 41 - 45)",
        "45": "Lesser Gods (Lvl 41 - 45)",
        "46": "Greater Gods (Lvl 46 - 50)",
        "47": "Greater Gods (Lvl 46 - 50)",
        "48": "Greater Gods (Lvl 46 - 50)",
        "49": "Greater Gods (Lvl 46 - 50)",
        "50": "Greater Gods (Lvl 46 - 50)",
        "51": "Assembly of the Seven (Lvl 51+)",
        "52": "God",
    }.get(x, "")


class LevelException(Exception):
    ...


class Level(commands.Cog, name="Level"):
    """
    Classe para cuidar dos eventos de level
    """

    def __init__(self, bot):
        self.bot = bot

    async def set_discord_role(self, role_name: str, discord_user: discord.Member, guild: discord.Guild):
        role = get(guild.roles, name=role_name)
        await discord_user.add_roles(role)

    async def update_discord_role(self, discord_user: discord.Member, user: User, guild: discord.Guild):
        """Atualiza cargo"""
        current_role_name = switch(str(user.level_id))
        new_role_name = switch(str(user.level_id + 1))
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

        if self.bot.bonusXP:
            experience *= 2

        async with self.bot.session as session:
            await UserRepository(session).update(pk=user.id, data={"experience": user.experience + experience})

    async def evolve_user(self, user: User, discord_user: discord.Member, guild: discord.Guild) -> tuple[bool, int]:
        experience_required = await self.prox_nivel(user.level_id)
        if user.experience >= experience_required and user.level_id < MAX_LEVEL:
            async with self.bot.session as session:
                user: User = await UserRepository(session).update(pk=user.id, data={"level_id": user.level_id + 1})
                await self.update_discord_role(discord_user=discord_user, user=user, guild=guild)
                session.refresh(user)
                return True, user.level_id
        return False, user.level_id

    async def insert_user(self, guild: discord.Guild, author: discord.Member) -> User:
        log.info("Inserindo usuário")
        async with self.bot.session as session:
            servers: ScalarResult[Server] = await ServerRepository(session).filter(discord_id=str(guild.id))
            server = servers.first()

            if not server:
                error = f"Servidor {guild.name} não encontrado"
                log.error(error)
                raise LevelException(error)

            data = {
                "name": author.name,
                "discord_user_id": str(author.id),
                "server_id": server.id,
                "level_id": 1,
                "experience": 0,
                "total_messages": 0,
                "updated_at": datetime.now(),
            }
            user: User = await UserRepository(session).create(data=data)
            log.info(f"Usuário {user.name} adicionado!")
            await self.set_discord_role(role_name="Rookies (lvl 1 - 5)", discord_user=author, guild=guild)
            return user

    async def update_total_messages(self, message: discord.Message) -> None:
        """soma 1 na quantidade de mensagens do usuario"""
        async with self.bot.session as session:
            users: ScalarResult[User] = await UserRepository(session).filter(
                discord_user_id=str(message.author.id), load_relationship=True
            )
            user = users.first()
            await self.set_discord_role(role_name="Rookies (lvl 1 - 5)", discord_user=message.author, guild=message.guild)

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

        async with self.bot.session as session:
            users: ScalarResult[User] = await UserRepository(session).filter(
                discord_user_id=str(ctx.author.id), load_relationship=True
            )
            user = users.first()

            if not user:
                await ctx.send("Usuário não encontrado")

            if user.server.discord_id != str(ctx.guild.id):
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

            embed.add_field(name="Level atual", value=f"{user.level_id} - {user.level.name}")
            embed.add_field(name="Exp atual", value=user.experience)
            embed.add_field(
                name="Próximo nível em",
                value=str(
                    int(
                        (await self.prox_nivel(user.level_id))
                        - user.experience
                    )
                ),
            )
            embed.set_footer(
                text=switchGuild(ctx.guild.id),
                icon_url="https://cdn.discordapp.com/avatars/596088044877119507/0d26138b572e7dfffc6cab54073cdb31.webp",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    """Adiciona cog ao bot"""
    await bot.add_cog(Level(bot))
