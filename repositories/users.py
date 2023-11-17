from models import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User
