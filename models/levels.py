from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship

from models.base import BaseModel


class Level(BaseModel):
    __tablename__ = "levels"

    name: Mapped[str]
    value: Mapped[int]
    users: Mapped[list["User"]] = relationship("User", back_populates="level", lazy="select")
