from abc import ABC

from sqlalchemy import ScalarResult, delete, insert, inspect, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import BaseModel


class BaseRepository(ABC):
    model: type[BaseModel]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> BaseModel:
        statement = insert(self.model).returning(self.model)
        result = await self.db.scalars(statement, [data])
        await self.db.commit()
        return result.first()

    async def filter(self, load_relationship: bool = False, **kwargs) -> ScalarResult:
        statement = select(self.model).filter_by(**kwargs)

        if load_relationship:
            fields = await self._get_model_relationship_fields()
            options = []
            for field in fields:
                options.append(selectinload(field))
            statement = statement.options(*options)

        result = await self.db.execute(statement)
        return result.scalars()

    async def update(self, pk: int, data: dict) -> BaseModel:
        statement = update(self.model).filter(self.model.id == pk).values(**data).returning(self.model)
        await self.db.execute(statement)
        await self.db.commit()
        result = await self.db.scalars(statement)
        return result.first()

    async def delete(self, pk: int):
        statement = delete(self.model).filter(self.model.id == pk)
        await self.db.execute(statement)
        await self.db.commit()

    async def _get_model_relationship_fields(self) -> list:
        return [field for field in inspect(self.model).relationships]
