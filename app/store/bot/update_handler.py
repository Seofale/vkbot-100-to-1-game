import typing
from functools import wraps
from logging import getLogger
if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.store.bot.updates import UpdateMessage, UpdateEvent, Update
from app.store.bot.constants import (
    BotTextCommands, BotMessages, BotEventCommands
)
from app.store.bot.keyboards import join_keyboard


def filter_game(needed: bool):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            upd: Update = list(kwargs.values())[0]
            game_exists = await upd.game.exists()
            if game_exists:
                await upd.game.init()
            if game_exists is needed:
                await func(*args, **kwargs)
        return wrapper
    return decorator


def init_user(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        upd: Update = list(kwargs.values())[0]
        await upd.user.init()
        await func(*args, **kwargs)
    return wrapper


class UpdateHandler:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("update_handler")

    async def handle_message(self, upd_msg: UpdateMessage):
        text = upd_msg.text
        match text:
            case BotTextCommands.get_info:
                await self.get_info(upd_msg=upd_msg)
            case BotTextCommands.create_game:
                await self.create_game(upd_msg=upd_msg)
            case _:
                await self.handle_answer(upd_msg=upd_msg)

    async def handle_event(self, upd_event: UpdateEvent):
        command = upd_event.payload.get("command")
        match command:
            case BotEventCommands.join:
                await self.join_player(upd_event=upd_event)

    async def get_info(self, upd_msg: UpdateMessage):
        await upd_msg.answer(text=BotMessages.info)

    @filter_game(needed=False)
    @init_user
    async def create_game(self, upd_msg: UpdateMessage):
        await upd_msg.game.create()
        await upd_msg.game.create_user(user=upd_msg.user)

        await upd_msg.answer(
            text=BotMessages.create,
            keyboard=join_keyboard(),
        )
        await upd_msg.game.back_timer()

        question = await upd_msg.game.get_active_question()
        await upd_msg.answer(text=question.title)

    @filter_game(needed=True)
    @init_user
    async def join_player(self, upd_event: UpdateEvent):
        user_in_game = await upd_event.game.check_user_in_game(
            user=upd_event.user,
        )
        if not user_in_game:
            await upd_event.game.create_user(user=upd_event.user)
            await upd_event.show_snackbar(text=BotMessages.already_join)
            return

        await upd_event.show_snackbar(text=BotMessages.already_join)

    @filter_game(needed=True)
    async def handle_answer(self, upd_msg: UpdateMessage):
        if not await upd_msg.user.get():
            return
        if not await upd_msg.game.check_user_in_game(user=upd_msg.user):
            return

        answer = await upd_msg.game.get_answer(title=upd_msg.text)
        if not answer:
            await upd_msg.game.add_fail(user=upd_msg.user)
            await upd_msg.answer(
                text=BotMessages.user_failed.format(
                    user=upd_msg.user.full_name,
                ),
            )

            user_lost = await upd_msg.game.check_user_lost(user=upd_msg.user)
            if user_lost:
                await upd_msg.answer(
                    text=BotMessages.user_lost.format(
                        user=upd_msg.user.full_name
                    ),
                )
        else:
            await upd_msg.game.add_points(
                user=upd_msg.user,
                score=answer.score,
            )
            await upd_msg.answer(
                text=BotMessages.user_right.format(
                    user=upd_msg.user.full_name,
                    score=answer.score,
                )
            )

        next_question = await upd_msg.game.get_next_question()
        if next_question:
            await upd_msg.answer(text=next_question.title)
            return

        await upd_msg.game.end()
        winner = await upd_msg.game.get_winner()
        await upd_msg.answer(
            text=BotMessages.end_game(
                user=winner.full_name,
                score=winner.score,
            )
        )
