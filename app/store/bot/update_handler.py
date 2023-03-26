import typing
from logging import getLogger
if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.store.vk_api.dataclasses import UpdateMessage, UpdateEvent
from app.store.bot.message import Message
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
            case _:
                await self.handle_answer(update_message=update_message)

    async def handle_event(self, update_event: UpdateEvent):
        command = update_event.payload.get("command")
        match command:
            case BotEventCommands.join:
                await self.join_player(update_event=update_event)

    async def get_info(self, update_message: UpdateMessage):
        message = Message(
            app=self.app,
            peer_id=update_message.peer_id,
            text=BotMessages.info,
        )
        await message.send()

    async def create_game(self, update_message: UpdateMessage):
        game = await self.app.store.game.get_game_by_peer_id(
            peer_id=update_message.peer_id,
        )
        if game:
            self.logger.error("Game already exists!")
            return

        user = await self.logic_helper.get_or_create_user(
            vk_id=update_message.from_id,
        )
        game = await self.app.store.game.create_game(
            peer_id=update_message.peer_id,
        )
        await self.app.store.game.create_user_statistics(
            user_id=user.id,
            game_id=game.id,
        )

        message = Message(
            app=self.app,
            peer_id=update_message.peer_id,
            text=BotMessages.create,
            keyboard=join_keyboard(),
        )
        await message.send()

        await self.logic_helper.back_timer(update_message=update_message)

        await self.logic_helper.start_game(
            update_message=update_message,
            game_id=game.id,
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

    async def handle_answer(self, update_message: UpdateMessage):
        game = await self.app.store.game.get_game_by_peer_id(
            peer_id=update_message.peer_id,
        )
        if not game:
            return
        user = await self.app.store.game.get_user(
            vk_id=update_message.from_id,
        )
        if not user:
            return

        now_question = await self.app.store.game.get_active_question(
            game_id=game.id,
        )
        answer = await self.app.store.game.get_answer_by_title_and_question_id(
            title=update_message.text.lower(),
            question_id=now_question.id,
        )

        if not answer:
            await self.app.store.game.add_fail_to_user(
                game_id=game.id,
                user_id=user.id,
            )
            await self.app.store.game.get_user_statistics(
                game_id=game.id,
                user_id=user.id,
            )
            message = Message(
                app=self.app,
                peer_id=update_message.peer_id,
                text=BotMessages.user_failed.format(user=user.full_name),
            )
            await message.send()

            failures_count = await self.app.store.game.get_user_failures_count(
                game_id=game.id,
                user_id=user.id,
            )
            if failures_count == 3:
                await self.app.store.game.make_user_lost(
                    game_id=game.id,
                    user_id=user.id,
                )
                message = Message(
                    app=self.app,
                    peer_id=update_message.peer_id,
                    text=BotMessages.user_lost.format(user=user.full_name),
                )
                await message.send()
        else:
            await self.app.store.game.add_points_to_user(
                game_id=game.id,
                user_id=user.id,
                score=answer.score,
            )
            message = Message(
                app=self.app,
                peer_id=update_message.peer_id,
                text=BotMessages.user_right.format(
                    user=user.full_name,
                    points=answer.score,
                ),
            )
            await message.send()

        next_question_exists = await self.app.store.game.move_to_next_question(
            game_id=game.id,
        )
        if not next_question_exists:
            await self.app.store.game.end_game(
                peer_id=update_message.peer_id,
            )
            winner = await self.app.store.game.get_winner_with_score(
                game_id=game.id,
            )
            message = Message(
                app=self.app,
                peer_id=update_message.peer_id,
                text=BotMessages.end_game.format(
                    user=winner.full_name,
                    points=winner.score,
                )
            )
            await message.send()
            return

        next_question = await self.app.store.game.get_active_question(
            game_id=game.id,
        )
        message = Message(
            app=self.app,
            peer_id=update_message.peer_id,
            text=next_question.title,
        )
        await message.send()
