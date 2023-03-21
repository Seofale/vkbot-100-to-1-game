import typing
import asyncio
from logging import getLogger

from app.store.vk_api.dataclasses import Message, UpdateMessage
from app.store.bot.constants import BotMessages

if typing.TYPE_CHECKING:
    from app.web.app import Application


class LogicHelper:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("update_handler")

    async def get_or_create_user(self, vk_id: int):
        user = await self.app.store.game.get_user(
            vk_id=vk_id,
        )
        if not user:
            user = await self.app.store.game.create_user(
                vk_id=vk_id,
            )
        return user

    async def back_timer(
        self,
        update_message: UpdateMessage,
        seconds: int = 10,
    ):
        await self.app.store.vk_api.send_message(
            message=Message(
                peer_id=update_message.peer_id,
                text=BotMessages.back_timer.format(seconds),
            )
        )
        counter = seconds
        while counter > 1:
            counter -= 1
            await asyncio.sleep(1)
            await self.app.store.vk_api.edit_message(
                message=Message(
                    peer_id=update_message.peer_id,
                    text=BotMessages.back_timer.format(counter)
                ),
                conversation_message_id=update_message.
                conversation_message_id + 2,
            )
        await self.app.store.vk_api.edit_message(
            message=Message(
                peer_id=update_message.peer_id,
                text=BotMessages.time_over,
            ),
            conversation_message_id=update_message.
            conversation_message_id + 2,
        )
