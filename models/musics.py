from sqlalchemy.orm import Mapped

import models


class Music(models.BaseModel):
    __tablename__ = "musics"

    name: Mapped[str]
    url: Mapped[str]
    user_id: Mapped[int]
    title: Mapped[str | None]
