import typing
from logging import getLogger
if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.store.vk_api.dataclasses import Message, UpdateMessage, UpdateEvent
from app.store.bot.constants import (
    BotTextCommands, BotMessages, BotEventCommands
)
from app.store.bot.logic_helper import LogicHelper
from app.store.bot.keyboards import join_keyboard


class UpdateHandler:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("update_handler")
        self.logic_helper = LogicHelper(app)

    async def handle_message(self, update_message: UpdateMessage):
        text = update_message.text
        match text:
            case BotTextCommands.get_info:
                await self.get_info(update_message=update_message)
            case BotTextCommands.create_game:
                await self.create_game(update_message=update_message)

    async def handle_event(self, update_event: UpdateEvent):
        command = update_event.payload.get("command")
        match command:
            case BotEventCommands.join:
                await self.join_player(update_event=update_event)

    async def get_info(self, update_message: UpdateMessage):
        await self.app.store.vk_api.send_message(
            message=Message(
                peer_id=update_message.peer_id,
                text=BotMessages.info,
            )
        )

    async def create_game(self, update_message: UpdateMessage):
        game = await self.app.store.game.get_game_by_peer_id(
            peer_id=update_message.peer_id,
        )
        if game:
            return

        user = await self.logic_helper.get_or_create_user(
            vk_id=update_message.from_id,
        )
        game = await self.app.store.game.create_game(
            peer_id=update_message.peer_id,
        )

        await self.app.store.vk_api.send_message(
            message=Message(
                peer_id=update_message.peer_id,
                text=BotMessages.create,
                keyboard=join_keyboard(),
            )
        )

        await self.logic_helper.back_timer(update_message=update_message)

        await self.app.store.vk_api.edit_message(
            message=Message(
                peer_id=update_message.peer_id,
                text=BotMessages.create,
            ),
            conversation_message_id=update_message.conversation_message_id + 1,
        )

        await self.app.store.game.create_user_statistics(
            user_id=user.id,
            game_id=game.id,
        )

        await self.app.store.vk_api.send_message(
            message=Message(
                peer_id=update_message.peer_id,
                text=BotMessages.start,
            )
        )

    async def join_player(self, update_event: UpdateEvent):
        game = await self.app.store.game.get_game_by_peer_id(
            peer_id=update_event.peer_id,
        )
        if not game:
            return

        user = await self.logic_helper.get_or_create_user(
            vk_id=update_event.user_id,
        )
        user_in_game = await self.app.store.game.get_user_statistics(
            game_id=game.id,
            user_id=user.id,
        )
        if not user_in_game:
            await self.app.store.game.create_user_statistics(
                game_id=game.id,
                user_id=user.id,
            )
            await self.app.store.vk_api.show_snackbar(
                event=update_event,
                text=BotMessages.user_join,
            )
            return

        await self.app.store.vk_api.show_snackbar(
            event=update_event,
            text=BotMessages.already_join,
        )
