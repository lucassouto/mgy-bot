from models import Server
from repositories.base import BaseRepository


class ServerRepository(BaseRepository):
    model = Server
