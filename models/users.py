from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

import models


class User(models.BaseModel):
    __tablename__ = "users"

    name: Mapped[str]
    discord_user_id: Mapped[str]
    level: Mapped["models.Level"] = relationship("Level", back_populates="users")
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"))
    experience: Mapped[int]
    server: Mapped["models.Server"] = relationship("Server", back_populates="users")
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"))
    youtube: Mapped[str | None]
    twitch: Mapped[str | None]
    twitter: Mapped[str | None]
    others: Mapped[str | None]
    total_messages: Mapped[int | None]
