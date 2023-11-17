from models import Music
from repositories.base import BaseRepository


class MusicRepository(BaseRepository):
    model = Music
