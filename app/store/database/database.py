from typing import TYPE_CHECKING, Any
from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession,
    create_async_engine, async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase

from app.store.database import Base

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: AsyncEngine | None = None
        self._db: DeclarativeBase | None = None
        self.session: AsyncSession | None = None

    async def connect(self, *args: Any, **kwargs: Any) -> None:
        self._db = Base
        self._engine = create_async_engine(
            "postgresql+asyncpg://{}:{}@{}/{}".format(
                self.app.config.database.user,
                self.app.config.database.password,
                self.app.config.database.host,
                self.app.config.database.database,
            ),
        )
        self.session = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
        )

    async def disconnect(self, *args: Any, **kwargs: Any) -> None:
        if self._engine:
            await self._engine.dispose()
