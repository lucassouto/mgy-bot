from sqlalchemy import Column, ForeignKey, Table

from models import BaseModel

UserServer = Table(
    "user_servers",
    BaseModel.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("server_id", ForeignKey("servers.id"), primary_key=True),
)
