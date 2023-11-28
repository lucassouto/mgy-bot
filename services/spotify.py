import logging

from decouple import config
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

log = logging.getLogger("youtube")


class SpotifyClient(Spotify):
    def __init__(self):
        super().__init__(
            auth_manager=SpotifyClientCredentials(
                client_id=config("SPOTIPY_CLIENT_ID"),
                client_secret=config("SPOTIPY_CLIENT_SECRET"),
            )
        )

    async def extract_playlist_to_youtube(self, link: str) -> list[str]:
        """Separa musicas da playlist para api do youtube v3"""
        tracks = []
        fields = "items.track.name,items.track.artists.name"
        offset = 0

        # A conexão com o spotify as vezes reseta, implementar retry
        tries = 0
        while tries <= 3:
            try:
                tries += 1

                response = self.playlist_items(playlist_id=link, fields=fields)

                items = response["items"]
                while len(response["items"]) >= 100:
                    offset += 100
                    response = self.playlist_items(
                        playlist_id=link,
                        offset=offset,
                        limit=100,
                        fields=fields,
                    )
                    items.extend(response["items"])

                tracks.extend([f"{item['track']['artists'][0]['name']} {item['track']['name']}" for item in items])
            except Exception:
                log.exception("Erro ao adquirir musicas da playlist, tentando novamente.")
                continue
            else:
                break

        return tracks
