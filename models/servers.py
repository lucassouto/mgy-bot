from sqlalchemy.orm import Mapped, relationship

import models


class Server(models.BaseModel):
    __tablename__ = "servers"

    name: Mapped[str]
    discord_id: Mapped[str]
    users: Mapped[list["models.User"]] = relationship("User", back_populates="server")
