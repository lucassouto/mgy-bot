import asyncio
import logging

import discord
import yt_dlp

log = logging.getLogger("youtube")

# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda: ""


class YTDLSource(discord.PCMVolumeTransformer):
    """
    Classe para definir parametros do YTDL
    """

    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn -sn -dn",
    }
    FFMEPG_OPTIONS_LOUDNORM = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn -sn -dn -filter:a loudnorm",
    }

    def __init__(self, source, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.title: str = data.get("title")
        self.duration: int = data.get("duration")
        self.url: str = data.get("url")

    @classmethod
    def yt_dl(cls):
        format_options = {
            "format": "bestaudio/best",
            "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
            "restrictfilenames": True,
            "noplaylist": True,
            "playlistrandom": True,
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "logtostderr": False,
            "quiet": True,
            "no_warnings": True,
            "default_search": "auto",
            # bind to ipv4 since ipv6 addresses cause issues sometimes
            "source_address": "0.0.0.0",
            "verbose": True,
            "cookiefile": "cookies.txt",
        }

        return yt_dlp.YoutubeDL(params=format_options)

    @classmethod
    async def from_url(cls, queue: dict, url: str, *, loop=None, stream=False) -> tuple:
        """Retira informações da url"""
        loop = loop or asyncio.get_event_loop()
        yt_dl = cls.yt_dl()

        try:
            data = await loop.run_in_executor(None, lambda: yt_dl.extract_info(url, download=not stream))

            # Search for a valid item in the queue
            while not data:
                if queue[1]:
                    queue.pop(0)
                    url = queue[0]
                    data = await loop.run_in_executor(None, lambda: yt_dl.extract_info(url, download=not stream))
                else:
                    return None, None
                if not data:
                    await asyncio.sleep(2)  # Delay to avoid too many requests
        except IndexError:
            log.exception("Lista vazia")
            return None, None
        except Exception:
            log.exception("Erro ao adquirir video, tentando encontrar nova na lista.")
            raise

        # Useful for searching by song name
        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else yt_dl.prepare_filename(data)
        return filename, data
