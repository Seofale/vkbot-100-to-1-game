import typing
from app.store.bot.keyboards import Keyboard

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Message:
    def __init__(
        self,
        app: "Application",
        peer_id: int,
        text: str,
        keyboard: Keyboard | str = "",
    ):
        self.app = app
        self.peer_id = peer_id
        self.text = text
        self.keyboard = keyboard
        self.cmd = None

    async def send(self):
        self.cmd = await self.app.store.vk_api.send_message(
            peer_id=self.peer_id,
            text=self.text,
            keyboard=self.keyboard,
        )

    async def edit(self, text: str):
        await self.app.store.vk_api.edit_message(
            peer_id=self.peer_id,
            text=text,
            cmd=self.cmd,
        )
