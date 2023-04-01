import typing

from app.store.bot.game import Game
from app.store.bot.user import User
from app.store.bot.keyboards import Keyboard

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Update:
    def __init__(
        self,
        app: "Application",
        peer_id: int,
        user_id: int,
        event_id: int,
    ):
        self.app = app
        self.peer_id = peer_id
        self.user_id = user_id
        self.event_id = event_id
        self.game = Game(
            app=app,
            peer_id=peer_id,
        )
        self.user = User(
            app=app,
            vk_id=user_id,
        )


class UpdateMessage(Update):
    def __init__(
        self,
        app: "Application",
        peer_id: int,
        user_id: int,
        event_id: int,
        text: str,
        cmd: int,
    ):
        super().__init__(
            app=app,
            peer_id=peer_id,
            user_id=user_id,
            event_id=event_id,
        )
        self.text = text
        self.cmd = cmd

    async def answer(self, text: str, keyboard: Keyboard | str = ""):
        await self.app.store.vk_api.send_message(
            peer_id=self.peer_id,
            text=text,
            keyboard=keyboard,
        )


class UpdateEvent(Update):
    def __init__(
        self,
        app: "Application",
        peer_id: int,
        user_id: int,
        event_id: int,
        payload: str,
    ):
        super().__init__(
            app=app,
            peer_id=peer_id,
            user_id=user_id,
            event_id=event_id,
        )
        self.payload = payload

    async def show_snackbar(self, text: str):
        await self.app.store.vk_api.show_snackbar(
            event_id=self.event_id,
            user_id=self.user_id,
            peer_id=self.peer_id,
            text=text,
        )
