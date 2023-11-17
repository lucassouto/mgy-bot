from sqlalchemy.orm import Mapped, relationship

import models


class Level(models.BaseModel):
    __tablename__ = "levels"

    name: Mapped[str]
    value: Mapped[int]
    users: Mapped[list["models.User"]] = relationship("User", back_populates="level", lazy="select")
