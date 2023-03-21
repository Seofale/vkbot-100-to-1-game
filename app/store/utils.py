from typing import Callable
from functools import wraps

from app.base.base_accessor import BaseAccessor


def decorate_all_methods(decorator: Callable):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate


def add_db_session_to_accessor(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        self: BaseAccessor = args[0]
        async with self.app.database.session.begin() as session:
            kwargs["session"] = session
            result = await func(*args, **kwargs)
        return result
    return wrapper
