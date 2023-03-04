from typing import Optional, TYPE_CHECKING
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
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[DeclarativeBase] = None
        self.session: Optional[AsyncSession] = None

    async def connect(self, *_: list, **__: dict) -> None:
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

    async def disconnect(self, *_: list, **__: dict) -> None:
        if self._engine:
            await self._engine.dispose()
