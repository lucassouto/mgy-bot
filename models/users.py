
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name: Mapped[str]
    discord_user_id: Mapped[str]
    level = relationship("Level", back_populates="users")
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"))
    experience: Mapped[int]
    server = relationship("Server", back_populates="users")
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"))
    youtube: Mapped[Optional[str]]
    twitch: Mapped[Optional[str]]
    twitter: Mapped[Optional[str]]
    others: Mapped[Optional[str]]
    total_messages: Mapped[Optional[int]]
