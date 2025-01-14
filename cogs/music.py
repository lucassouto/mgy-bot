"""
    Modulo para comandos de musica
"""
from __future__ import annotations

import asyncio
import logging
import os
import random
import re
import sys
from urllib.parse import parse_qs, urlparse

import discord
import googleapiclient.discovery
from bs4 import BeautifulSoup
from discord.ext import commands, tasks

from services.spotify import SpotifyClient
from services.youtube import YTDLSource
from utils.functions import build_footer_infos
from utils.pgdatabase import Postgres

MAX_NUM = 100000

# Inicia o logger
log = logging.getLogger("music")


youtube = googleapiclient.discovery.build(
    "youtube",
    "v3",
    developerKey=os.environ["YOUTUBE_API_KEY"],
    cache_discovery=False,
)


def switch(guild_id: int):
    """Switch case para pegar macro"""
    return {
        470710752789921803: os.environ["MACRO"],
        582709300506656792: os.environ["MACRO2"],
    }.get(guild_id, "MGY")


class Music(commands.Cog):
    """
    Classe para comandos de musica
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pg = Postgres()
        self.title = {}  # titulo da musica por guild
        self.queue = {}  # lista de musica por guild
        self.global_vol = {}  # volume global
        self.message = {}  # mensagem 'playing' por guild
        self.guild_voice_client = {}  # lista de voice client de guild

    async def is_url(self, url: str):
        """Verifica se string é uma url"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    async def enableDoubleXP(self):
        """Habilita por 29 segundos Xp em dobro (Bonus Room)"""
        self.bot.bonus_xp = True
        await asyncio.sleep(29)
        self.bot.bonus_xp = False

    @tasks.loop(minutes=10.0)
    async def verifyalone(self):
        """Verifica se está sozinho no servidor e disconecta"""

        log.info("Verificando se o bot está sozinho")
        # Verifica todas as guilds salvas
        for guild_id in list(self.guild_voice_client):
            members = self.guild_voice_client[guild_id].channel.members
            if len(members) == 1:
                # Id do bot, ou seja, é o unico no canal de voz
                if members[0].id == 596088044877119507:
                    try:
                        log.info("Desconectando pois não existem membros online")
                        await self.guild_voice_client[guild_id].disconnect()
                        self.queue[guild_id].clear()
                        self.guild_voice_client.pop(guild_id)
                    except Exception:  # pylint: disable=broad-exception-caught
                        log.exception("Erro ao desconectar.")
            elif len(members) == 0:
                self.queue[guild_id].clear()
                self.guild_voice_client.pop(guild_id)
            else:
                log.info("%s : possui %s online", str(guild_id), str(len(members)))

        # Se não esta tocando em nenhuma guild, encerra a tarefa
        if not self.guild_voice_client or len(self.guild_voice_client) == 0:
            log.info("Tarefa encerrada")
            self.verifyalone.cancel()  # pylint: disable=no-member
        else:
            log.info(
                "%s guilds com membros no canal de voz",
                str(len(self.guild_voice_client)),
            )

    @commands.command(hidden=True)
    async def join(self, ctx: commands.Context, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    async def randomizequeue(self, ctx: commands.Context):
        """Aleatoariza a queue menos a primeira posicao"""
        if ctx.voice_client.is_playing():
            temp = self.queue[ctx.guild.id].pop(0)
            random.shuffle(self.queue[ctx.guild.id])
            self.queue[ctx.guild.id].insert(0, temp)
        else:
            random.shuffle(self.queue[ctx.guild.id])
        await ctx.send("```Alterado a ordem da lista de musica```")

    async def playlist(self, guild_id: int, pagina: int):
        """Separa musicas da playlist utilizando api do youtube v3"""

        log.info("Buscando videos da playlist: %i", pagina)
        query = parse_qs(urlparse(pagina).query, keep_blank_values=True)
        playlist_id = query["list"][0]

        # pylint: disable=no-member
        request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=50)
        response = request.execute()

        playlist_items = []
        while request is not None:
            response = request.execute()
            playlist_items += response["items"]
            request = youtube.playlistItems().list_next(request, response)  # pylint: disable=no-member

        videos = []
        log.info("Total videos: %s", str(len(playlist_items)))
        for t in playlist_items:
            videos.append("https://www.youtube.com/watch?v=" + t["snippet"]["resourceId"]["videoId"])

        for v in videos:
            self.queue[guild_id].append(v)
        log.info(self.queue)

    async def tocar(self, ctx: commands.Context):
        """Inicia a tocar audio"""

        # Executao ao finalizar uma musica
        def nextOrCleanUp(info):
            log.info("Song is done! Removing from queue. info: %s", str(info))

            # Retira a ultima musica tocada
            try:
                if self.queue[ctx.guild.id]:
                    self.queue[ctx.guild.id].pop(0)
            except Exception:  # pylint: disable=broad-exception-caught
                log.exception("Erro ao retirar da lista")

            if ctx.voice_client:
                # Se a lista não estiver vazia, toca o próximo, caso contrario disconecta
                if not self.queue[ctx.guild.id] and ctx.voice_client:
                    log.info("Queue empty, disconnecting")
                    coro = ctx.voice_client.disconnect()
                else:
                    log.info("Ready to play next song")
                    coro = self.tocar(ctx)
                fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
                try:
                    fut.result()
                except Exception:  # pylint: disable=broad-exception-caught
                    log.exception("After executado com erro!")

        if self.queue[ctx.guild.id]:
            async with ctx.typing():
                filename, data = await YTDLSource.from_url(
                    queue=self.queue[ctx.guild.id],
                    url=self.queue[ctx.guild.id][0],
                    loop=self.bot.loop,
                    stream=True,
                )
                player = YTDLSource(
                    source=discord.FFmpegPCMAudio(filename, **YTDLSource.FFMEPG_OPTIONS_LOUDNORM),
                    data=data,
                )
                footer_text, icon_url = build_footer_infos(ctx.guild.id)

                ctx.voice_client.play(player, after=nextOrCleanUp)

                # Bonus room
                if player.title == "Bonus Room Blitz - Donkey Kong Country":
                    self.enableDoubleXP()

                # Cria o volume global para a guild
                if ctx.guild.id not in self.global_vol:
                    self.global_vol[ctx.guild.id] = 50 / 100
                ctx.voice_client.source.volume = self.global_vol[ctx.guild.id]

                self.title[ctx.guild.id] = player.title
                log.info("Tocando %s", player.title)

                if player.duration:
                    time = float(player.duration)
                    minutes = time // 60
                    time %= 60
                    seconds = time
                else:
                    time = 24
                    minutes = 24
                    seconds = time
                if len(self.queue[ctx.guild.id]) > 1:
                    embed = discord.Embed(
                        description=(
                            f"[{player.title}] ({self.queue[ctx.guild.id][0]})\n "
                            f"Duração: {int(minutes):02d}:{int(seconds):02d}\n "
                            f"Ainda na lista: {len(self.queue[ctx.guild.id]) - 1}",
                        ),
                        colour=0xFA00D4,
                    )
                    embed.set_footer(
                        text=footer_text,
                        icon_url=icon_url,
                    )
                else:
                    embed = discord.Embed(
                        description=(
                            f"[{player.title}]({self.queue[ctx.guild.id][0]})\n "
                            f"Duração: {int(minutes):02d}:{int(seconds):02d}"
                        ),
                        colour=0xFA00D4,
                    )
                    embed.set_footer(
                        text=footer_text,
                        icon_url=icon_url,
                    )
                if self.message[ctx.guild.id]:
                    await self.message[ctx.guild.id].edit(embed=embed)
                else:
                    self.message[ctx.guild.id] = await ctx.send(embed=embed)

    @commands.command(aliases=["vol", "v", "volmax", "maxvol"])
    async def volume(self, ctx: commands.Context, *args):
        """Troca o volume.

        Args extra:
        -m para voume máximo.
        -r reseta volume padrão
        """
        # Garante que o edit esta apos ultimo comando para a guild
        self.message[ctx.guild.id] = None
        log.info("Alterando volume: %s", str(args))
        if ctx.voice_client is None:
            return await ctx.send("O bot não está conectado em um canal de voz.")
        volume = 50
        if args and args[0].isdigit() and int(args[0]) > 0:
            volume = int(args[0])

        if self.queue[ctx.guild.id][0] == "https://www.youtube.com/watch?v=Tu5-h4Ye0J0":
            ctx.voice_client.source.volume = sys.float_info.max
            await ctx.send("Lmao")
        elif ("-m" in args or "max" in args or "-max" in args) or (
            ctx.invoked_with.lower() == "volmax" or ctx.invoked_with.lower() == "maxvol"
        ):
            ctx.voice_client.source.volume = sys.float_info.max
            await ctx.send("Dale")
        elif "-r" in args or "reset" in args or "-reset" in args:
            ctx.voice_client.source.volume = 50 / 100
            await ctx.send("Volume resetado")
        else:
            ctx.voice_client.source.volume = volume / 100
            await ctx.send(f"Volume trocado para {volume}%")

    @commands.command(aliases=["gvol", "gv", "gvolmax", "gmaxvol", "alwaysvolmax"])
    async def globalvolume(self, ctx: commands.Context, *args):
        """Troca o volume.

        Args extra:
        -m para voume máximo.
        -r reseta volume padrão
        """

        # Garante que o edit esta apos ultimo comando para a guild
        self.message[ctx.guild.id] = None
        log.info("Alterando volume global para : %s", str(args))

        # Cria o volume global para a guild
        if ctx.guild.id not in self.global_vol:
            self.global_vol[ctx.guild.id] = 50 / 100

        volume = 50
        if args and args[0].isdigit() and int(args[0]) > 0:
            volume = int(args[0])

        if ("-m" in args or "max" in args or "-max" in args) or (
            ctx.invoked_with.lower() == "gvolmax"
            or ctx.invoked_with.lower() == "gmaxvol"
            or ctx.invoked_with.lower() == "alwaysvolmax"
        ):
            self.global_vol[ctx.guild.id] = sys.float_info.max
            volume = "max"
            await ctx.send("Dale Dale Dale")
        elif "-r" in args or "reset" in args or "-reset" in args:
            self.global_vol[ctx.guild.id] = 50 / 100
            volume = 50 / 100
            await ctx.send("Volume global resetado")
        else:
            self.global_vol[ctx.guild.id] = volume / 100
            await ctx.send(f"Volume global trocado para {volume}%")

        pending_command = self.bot.get_command("volume")
        await ctx.invoke(pending_command, str(volume))

    @commands.command(aliases=["paly", "ply", "p"])
    async def play(self, ctx: commands.Context, url: str, *args):
        """Toca a partir uma url ou pesquisa.

        Args opcionais:
        -shuffle - ordem aleatoria
        -n - numero de repetições
        """
        # (sem predownload)

        async with ctx.typing():
            # Garante que o edit esta apos ultimo comando para a guild
            self.message[ctx.guild.id] = None
            # Verifica se eh uma url, se nao for, completa o nome com args para pesquisa
            if not await self.is_url(url):
                for item in args:
                    if not item.startswith("-"):
                        url += " " + item
                if "-f" in args:
                    self.queue[ctx.guild.id].insert(1, url)
                else:
                    self.queue[ctx.guild.id].append(url)
            elif re.search("spotify", url):
                tracks = await SpotifyClient().extract_playlist_to_youtube(link=url)
                self.queue[ctx.guild.id].extend(tracks)
            elif re.search("playlist", url):
                await self.playlist(ctx.guild.id, url)
            elif "-f" in args:
                self.queue[ctx.guild.id].insert(1, url)
            else:
                self.queue[ctx.guild.id].append(url)

            # Argumentos extra
            for item in args:
                # Caso numero no fim, coloca n vezes na lista
                if item.startswith("-") and item[1:].isdigit():
                    log.info("Encontrado digito")
                    for i in range(1, int(item[1:])):
                        if i > MAX_NUM:
                            break
                        if "-f" in args:
                            self.queue[ctx.guild.id].insert(1, url)
                        else:
                            self.queue[ctx.guild.id].append(url)

            # Se shuffle no comando, altera a ordem da lista
            if "-shuffle" in args:
                await self.randomizequeue(ctx)

        # Se estiver tocando, adiciona a lista
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            log.info("Esta tocando, adicionando a queue")

            await ctx.send(f"```Adicionado à lista, posição: {len(self.queue[ctx.guild.id]) - 1}```")
        else:
            log.info("Nao esta tocando, comecando agora")

            await self.tocar(ctx)

    @commands.command(aliases=["paus", "pau"])
    async def pause(self, ctx: commands.Context):
        """Pausa a música"""
        if ctx.voice_client.is_playing():
            # Se for garagem da vizinha nao permite mudar o volume
            if self.queue[ctx.guild.id][0] == "https://www.youtube.com/watch?v=Tu5-h4Ye0J0":
                ctx.voice_client.source.volume = sys.float_info.max
                ctx.send("Lmao")
            else:
                ctx.voice_client.pause()
            await ctx.send(f"Pausado: `{self.title[ctx.guild.id]}`")

    @commands.command(aliases=["res"])
    async def resume(self, ctx: commands.Context):
        """Retorna a tocar música"""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send(f"Tocando: `{self.title[ctx.guild.id]}`")

    @commands.command(aliases=["skup", "ski", "next", "skyp"])
    async def skip(self, ctx: commands.Context, quantidade=1):
        """Pula para o próximo item da lista de músicas.

        Args opcionais:
        quantidade - total de músicas para dar skip
        """

        # nao permite dar skip na garagem da vizinha
        if self.queue[ctx.guild.id][0] == "https://www.youtube.com/watch?v=Tu5-h4Ye0J0":
            ctx.voice_client.source.volume = sys.float_info.max
            await ctx.send("Lmao")
            return

        if len(self.queue[ctx.guild.id]) > 1:
            if quantidade < 0:
                quantidade = 1

            for _ in range(quantidade - 1):
                if self.queue[ctx.guild.id]:
                    self.queue[ctx.guild.id].pop(0)

            log.info("Skip em %s", str(quantidade + 1))
            ctx.voice_client.stop()  # Já da stop na musica atual

        if len(self.queue[ctx.guild.id]) < 1:
            await ctx.send("`Não tem outras músicas na listas. Parando de tocar...`")

    @commands.command(aliases=["sto"])
    async def stop(self, ctx: commands.Context):
        """Desconecta o bot do canal de voz e limpa a lista de músicas"""
        # nao permite dar skip na garagem da vizinha

        try:
            if (
                self.queue[ctx.guild.id]
                and self.queue[ctx.guild.id][0] == "https://www.youtube.com/watch?v=Tu5-h4Ye0J0"
            ):
                ctx.voice_client.source.volume = sys.float_info.max
                await ctx.send("Lmao")
                return
            log.info("%s terminou de tocar", self.title[ctx.guild.id])
            if ctx.voice_client.is_playing() and self.title[ctx.guild.id] == "Quim Barreiros - A garagem da vizinha":
                ctx.voice_client.source.volume = sys.float_info.max
                await ctx.send("Lmao")
            else:
                await ctx.send("`Parando de tocar...`")
                self.queue[ctx.guild.id].clear()
                log.info("Desconectou terminou de tocar")
                await ctx.voice_client.disconnect()
        except Exception:  # pylint: disable=broad-exception-caught
            log.exception("Erro ao dar stop")
            await ctx.voice_client.disconnect()

    @commands.command(aliases=["list", "queue"])
    async def lista(self, ctx: commands.Context):
        """Exibe as 10 primeiras musicas da lista"""

        # Garante que o edit esta apos ultimo comando para a guild
        self.message[ctx.guild.id] = None

        log.info("Exibindo lista")
        if self.queue.get(ctx.guild.id):
            async with ctx.typing():
                lista = "```"
                j = 1

                for x in self.queue[ctx.guild.id]:
                    info = YTDLSource.yt_dl().extract_info(x, download=False)
                    titulo = (info.get("title") if info.get("title") else x) if info else "¯\\_(ツ)_/¯"
                    lista += str(j) + ": " + titulo + "\n"
                    j += 1

                    # Limita exibicao para 10 musicas
                    if j > 10:
                        break
            lista += "Tip: Quer tocar a musica 7? Use: mgy skip 6"
            lista += "```"
            # coloca play apos a lista
            self.message[ctx.guild.id] = None
            await ctx.send(lista)
        else:
            await ctx.send("```Lista vazia```")

    @commands.command(aliases=["mash", "mas", "mashup", "rmash"])
    async def mashups(self, ctx: commands.Context, *args):
        """Toca mashups.

        Args:
        num - numero do mashup. Se usado com -r será o total de mashups à tocar
        -r - para random mashups
        """
        # URL "https://www.dropbox.com/sh/kqtsijt5jyb5pzl/AABPrMl4zTBvF9BvESO45T1Ra"
        log.info("Iniciando busca por mashups")
        # TODO: Use Path().open()
        soup = BeautifulSoup(open("Dropbox.html", encoding="utf-8"), features="lxml")  # noqa: SIM115,PTH123

        # pega todos os links da pagina
        mashups = []
        for link in soup.find_all("a"):
            mashups.append(link.get("href"))

        # retira links que nao sao musica
        mashups.pop(0)
        mashups.pop(0)
        mashups.pop(0)

        num = "1"
        if args and args[0].isdigit() and int(args[0]) > 0:
            num = str(args[0])
            if int(num) > MAX_NUM:
                num = str(MAX_NUM)
        else:
            return await ctx.send("```" + ctx.command.help + "```")

        # Toca aleatórios
        if "-r" in args or "r" in args or "random" in args:
            log.info("Tocando %s aleatorios", str(num))
            my_list = list(range(0, 342))  # list of integers from 0 to 342

            random.shuffle(my_list)  # aleatoriza a lista

            # coloca 'quantidade' ma lista
            for i in range(int(num)):
                self.queue[ctx.guild.id].append(mashups[my_list[i]])

            found = 1  # temp
        # Toca o mashup de numero num
        else:
            log.info("buscando num %s")
            found = 0
            # percorre os links, pega o nome e compara com o especificado
            log.info("Iniciando comparacao com o dropbox")
            for x in mashups:
                info = YTDLSource.yt_dl().extract_info(x, download=False)
                nome = info.get("title")
                achou = 1
                for i in range(len(num)):
                    if nome[i] != num[i]:
                        achou = 0  # nao encontrou
                        break
                if achou == 1:
                    log.info("Encontrou: %s", nome)
                    self.queue[ctx.guild.id].append(x)
                    found = 1  # encontrou
                    break

        # Verifica se foi encontrado
        if found == 1:
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                log.info("Esta tocando, adicionando a queue")
                await ctx.send(f"```Adicionado {num} à lista. Total na lista: {len(self.queue[ctx.guild.id]) - 1}```")
            else:
                log.info("Nao esta tocando, comecando agora")
                await self.tocar(ctx)
        else:
            log.info("Mashup numero: %s nao encontrado", num)
            await ctx.send("```Não encontrado```")

    @commands.command(aliases=["clear", "limpa", "clean"])
    async def limpar(self, ctx: commands.Context):
        """Limpa a lista de musicas"""
        try:
            temp = self.queue[ctx.guild.id][0]
            self.queue[ctx.guild.id].clear()
            self.queue[ctx.guild.id].append(temp)
            await ctx.send("```Lista limpa```")
        except Exception:  # pylint: disable=broad-exception-caught
            log.exception("Erro ao limpar a lista")

    @commands.command(aliases=["random", "randomize", "shuff"])
    async def shuffle(self, ctx: commands.Context):
        """Da uma shuffle na lista de musica"""
        await self.randomizequeue(ctx)

    @commands.command(aliases=["dk", "donkey", "kong", "bonus"])
    async def sdk(self, ctx: commands.Context, quantidade=5):
        """Shuffle 'n' donkey kong"""
        try:
            quan = int(quantidade)
            if quan < 0:
                quan = quan * -1
            if quan > MAX_NUM:
                quan = MAX_NUM
            for _ in range(0, quan):
                self.queue[ctx.guild.id].append("https://www.youtube.com/watch?v=8xEJOUfMIHo")
        except Exception:  # pylint: disable=broad-exception-caught
            log.exception("Erro ao atribuir quantidade")

        await self.randomizequeue(ctx)

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            log.info("Esta tocando, adicionando a queue")
            await ctx.send(
                f"```Adicionado {quantidade} Bonus Room à lista. Total na lista: {len(self.queue[ctx.guild.id]) - 1}```"
            )
        else:
            log.info("Nao esta tocando, comecando agora")
            await self.tocar(ctx)

    @commands.command(aliases=["t", "tocar"])
    async def toca(self, ctx: commands.Context, name: str, *args):
        """Toca link salvo.

        Verifique os links com: mgy mlinks.
        Args:
        -n - Numero de repetições
        -shuffle - Ordem aleatória

        Exemplo: mgy t garagem -24 -shuffle
        """

        # Consulta para buscar informacoes do usuario que enviou a mensagem
        sql = "select * from MUSIC_LINKS"
        sql += " WHERE NAME LIKE '" + str(name) + "%'"

        log.info("Buscando musica: %s", str(name))
        resultado = self.pg.query(sql)

        # Musica encontrada
        if resultado:
            url = resultado[0]["url"]
            # Verifica se eh uma url, se nao for, completa o nome com args para pesquisa
            if await self.is_url(url):
                if re.search("spotify", url):
                    tracks = await SpotifyClient().extract_playlist_to_youtube(link=url)
                    self.queue[ctx.guild.id].extend(tracks)
                elif re.search("playlist", url):
                    await self.playlist(ctx.guild.id, url)
                else:  # noqa: PLR5501
                    if "-f" in args:
                        self.queue[ctx.guild.id].insert(1, url)
                    else:
                        self.queue[ctx.guild.id].append(url)
            else:  # noqa: PLR5501
                if "-f" in args:
                    self.queue[ctx.guild.id].insert(1, url)
                else:
                    self.queue[ctx.guild.id].append(url)

            # Argumentos extra
            for item in args:
                if item.startswith("-") and item[1:].isdigit():
                    log.info("Encontrado digito")
                    for i in range(1, int(item[1:])):
                        if i > MAX_NUM:
                            break
                        if "-f" in args:
                            self.queue[ctx.guild.id].insert(1, url)
                        else:
                            self.queue[ctx.guild.id].append(url)
            # Se shuffle no comando, altera a ordem da lista
            if "-shuffle" in args:
                log.info("Aleatorio")
                await self.randomizequeue(ctx)

            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                log.info("Esta tocando, adicionando a queue")
                await ctx.send(
                    "```Adicionado {} à lista. Total na lista: {}```".format(
                        str(resultado[0]["name"]), len(self.queue[ctx.guild.id]) - 1
                    )
                )
            else:
                log.info("Nao esta tocando, comecando agora")
                await self.tocar(ctx)
        # Musica nao encontrada
        else:
            await ctx.send("Nome não encontrado. Você pode verificar os links existentes com: mgy musiclinks")
            await ctx.voice_client.disconnect()

    @commands.command()
    async def add(self, ctx: commands.Context, name: str, url: str):
        """Cria comando para tocar uma musica.

        Usado em conjunto com o comando 'tocar'.
        Exemplo: mgy add garagem link. Em seguida utilize: mgy t garagem"""

        # Consulta para buscar informacoes do usuario que enviou a mensagem
        async with ctx.typing():
            if len(name) > 20:
                return await ctx.send("Nome muito longo, use até 20 caracteres")
            sql = "select * from MUSIC_LINKS"
            sql += " WHERE NAME = '" + str(name) + "'"

            log.info("Buscando musica: %s", str(name))
            resultado = self.pg.query(sql)

            # Musica encontrada
            if resultado:
                ctx.send("Nome já existe. Você pode verificar os links existentes com: mgy musiclinks")

            # Musica nao encontrada
            else:  # noqa: PLR5501
                # Verifica se eh uma url, se nao for, completa o nome com args para pesquisa
                if not await self.is_url(url):
                    await ctx.send("Url invalida")
                    return
                else:
                    sql = "select ID_USUARIOS from USUARIOS"
                    sql += " WHERE USER_ID_DISCORD = '" + str(ctx.author.id) + "'"

                    log.info("Buscando musica: %s", str(name))
                    resultado = self.pg.query(sql)
                    if resultado:
                        info = YTDLSource.yt_dl().extract_info(url, download=False)
                        titulo = " "
                        if info and info.get("title"):
                            titulo = info.get("title")

                        sql = "insert into MUSIC_LINKS (NAME, URL, USER_ID, TITLE)"
                        sql += (
                            " values ('"
                            + str(name)
                            + "', '"
                            + str(url)
                            + "', '"
                            + str(resultado[0]["id_usuarios"])
                            + "', '"
                            + str(titulo)
                            + "')"
                        )
                        try:
                            self.pg.update(sql)
                            await ctx.send("Adicionado " + str(name) + ". Para tocar use: mgy t " + str(name))
                        except Exception:  # pylint: disable=broad-exception-caught
                            log.exception("Erro ao adicionar link")

    @commands.command(aliases=["mlist", "mlinks", "links"])
    async def musiclinks(self, ctx: commands.Context):
        """Mostra os comandos de musica criados"""
        # https://cog-creators.github.io/discord-embed-sandbox/
        async with ctx.typing():
            sql = "select * from MUSIC_LINKS"
            resultado = self.pg.query(sql)
            if resultado:
                lista = []
                titulo = []

                for x in resultado:
                    lista.append("[" + str(x["name"]) + "]" + "(" + str(x["url"]) + ")" + "\n")
                    if x["title"]:
                        titulo.append(str(x["title"]) + "\n")
                    else:
                        titulo.append("Não encontrado \n")
                i = 0
                name = ""
                title = ""
                while i < len(lista):
                    name += lista[i]
                    title += titulo[i]
                    if i != 0 and i % 10 == 0:
                        embed = discord.Embed(colour=0xFA00D4)

                        embed.add_field(name="Nome", value=name, inline=True)
                        embed.add_field(
                            name="Titulo",
                            value=title,
                            inline=True,
                        )
                        await ctx.send(embed=embed)

                        title = ""
                        name = ""
                    i += 1

                embed = discord.Embed(colour=0xFA00D4)

                if name != "":
                    embed.add_field(name="Nome", value=name, inline=True)
                    embed.add_field(name="Titulo", value=title, inline=True)

                embed.set_footer(
                    text="Para tocar use: mgy t nome. Com nome sendo um dos mostrados acima, use -shuffle para shuffle",
                    icon_url="https://cdn.discordapp.com/avatars/596088044877119507/0d26138b572e7dfffc6cab54073cdb31.webp",
                )

                await ctx.send(embed=embed)

    @play.before_invoke
    @mashups.before_invoke
    @sdk.before_invoke
    @toca.before_invoke
    async def ensure_voice(self, ctx: commands.Context):
        """Garante que o bot esta conectado em um canal de voz e queue existe para a guild"""
        # Cria a queue para a guild
        if ctx.guild.id not in self.queue:
            self.queue[ctx.guild.id] = []

        # Garante que o edit esta apos ultimo comando para a guild
        self.message[ctx.guild.id] = None

        # Cria variavel titulo para a guild
        self.title[ctx.guild.id] = ""

        if ctx.voice_client is None:
            if ctx.author.voice:
                # guarda o voice client para utilizar no verify alone
                self.guild_voice_client[ctx.guild.id] = await ctx.author.voice.channel.connect()

                try:
                    if not self.verifyalone.is_running():  # pylint: disable=no-member
                        self.verifyalone.start()  # pylint: disable=no-member
                except Exception:  # pylint: disable=broad-exception-caught
                    log.exception("Erro ao inicar tarefa em background")
            else:
                log.warning("Autor nao conectado no canal de voz")
                await ctx.send("Você não está conectado em um canal de voz")
                raise commands.CommandError("Author not connected to a voice channel.")  # Remove this


async def setup(bot: commands.Bot):
    """Adiciona o cog ao bot"""
    await bot.add_cog(Music(bot))
