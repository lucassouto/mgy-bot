from typing import Optional
from sqlalchemy.orm import Mapped

from models.base import BaseModel


class Music(BaseModel):
    __tablename__ = "musics"

    name: Mapped[str]
    url: Mapped[str]
    user_id: Mapped[int]
    title: Mapped[Optional[str]]
