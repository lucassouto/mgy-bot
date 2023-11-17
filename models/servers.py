from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from models.base import BaseModel


class Server(BaseModel):
    __tablename__ = "servers"

    name: Mapped[str]
    discord_id: Mapped[str]
    users: Mapped[list["User"]] = relationship("User", back_populates="server")
