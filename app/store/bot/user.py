import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application


class User:
    def __init__(self, app: "Application", vk_id: int):
        self._app = app
        self.vk_id = vk_id
        self.id: int = None
        self.first_name: str = None
        self.last_name: str = None
        self.score: int = None

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    async def init(self):
        user_data = await self._app.store.game.get_user(vk_id=self.vk_id)
        if not user_data:
            user_data = await self._app.store.game.create_user(
                vk_id=self.vk_id,
            )
        self.id = user_data.id
        self.first_name = user_data.first_name
        self.last_name = user_data.last_name

    async def get(self) -> bool:
        user_data = await self._app.store.game.get_user(vk_id=self.vk_id)
        if not user_data:
            return False
        self.id = user_data.id
        self.first_name = user_data.first_name
        self.last_name = user_data.last_name
        return True
