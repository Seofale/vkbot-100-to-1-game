import typing
import asyncio
from logging import getLogger

from app.store.vk_api.dataclasses import UpdateMessage
from app.store.bot.message import Message
from app.store.bot.constants import BotMessages
from app.game.dataclasses import UserDC

if typing.TYPE_CHECKING:
    from app.web.app import Application


class LogicHelper:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("update_handler")

    async def get_or_create_user(self, vk_id: int) -> UserDC:
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
        message = Message(
            app=self.app,
            peer_id=update_message.peer_id,
            text=BotMessages.back_timer.format(seconds=seconds),
        )
        await message.send()

        counter = seconds
        while counter > 1:
            counter -= 1
            await asyncio.sleep(1)
            await message.edit(
                text=BotMessages.back_timer.format(seconds=counter),
            )

        await message.edit(
            text=BotMessages.time_over,
        )

    async def start_game(
        self,
        update_message: UpdateMessage,
        game_id: int,
    ):
        message = Message(
            app=self.app,
            peer_id=update_message.peer_id,
            text=BotMessages.start,
        )
        await message.send()

        await self.back_timer(
            update_message=update_message,
            seconds=5,
        )

        first_question = await self.app.store.game.get_active_question(
            game_id=game_id,
        )
        message = Message(
            app=self.app,
            peer_id=update_message.peer_id,
            text=first_question.title,
        )
        await message.send()
