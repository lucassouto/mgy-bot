from sqlalchemy.orm import Mapped, relationship

import models
from models.user_servers import UserServer


class Server(models.BaseModel):
    __tablename__ = "servers"

    name: Mapped[str]
    discord_id: Mapped[str]
    users: Mapped[list["models.User"]] = relationship("User", secondary=UserServer, back_populates="servers")
