from models import UserServer
from repositories.base import BaseRepository


class UserServerRepository(BaseRepository):
    model = UserServer
