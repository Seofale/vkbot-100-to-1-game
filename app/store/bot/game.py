import typing
import asyncio

from app.store.bot.user import User
from app.store.bot.message import Message
from app.store.bot.constants import BotMessages
from app.game.dataclasses import QuestionDC, AnswerDC, UserDC

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Game:
    def __init__(self, app: "Application", peer_id: int):
        self._app = app
        self.peer_id = peer_id
        self.id = None
        self.in_process = False
        self.started_at = None

    async def create(self):
        game_data = await self._app.store.game.create_game(
            peer_id=self.peer_id,
        )
        self.id = game_data.id
        self.started_at = game_data.started_at

    async def init(self):
        game_data = await self._app.store.game.get_game_by_peer_id(
            peer_id=self.peer_id,
        )
        if game_data:
            self.id = game_data.id
            self.started_at = game_data.started_at
            self.in_process = game_data.in_process

    async def exists(self) -> bool:
        game_data = await self._app.store.game.get_game_by_peer_id(
            peer_id=self.peer_id,
        )
        if not game_data:
            return False
        return True

    async def check_user_in_game(self, user: User) -> bool:
        statistics_data = await self._app.store.game.get_user_statistics(
            game_id=self.id,
            user_id=user.id,
        )
        if statistics_data:
            return True
        return False

    async def create_user(self, user: User):
        await self._app.store.game.create_user_statistics(
            user_id=user.id,
            game_id=self.id,
        )

    async def back_timer(self, seconds: int = 10):
        message = Message(
            app=self._app,
            peer_id=self.peer_id,
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

    async def get_active_question(self) -> QuestionDC:
        question = await self._app.store.game.get_active_question(
            game_id=self.id,
        )
        return question

    async def get_answer(self, title: str) -> AnswerDC:
        active_q = await self.get_active_question()
        answer = await self._app.store.game.get_answer(
            title=title,
            question_id=active_q.id,
        )
        return answer

    async def add_fail(self, user: User):
        await self._app.store.game.add_fail_to_user(
            game_id=self.id,
            user_id=user.id,
        )

    async def add_points(self, user: User, score: int):
        await self._app.store.game.add_points_to_user(
            game_id=self.id,
            user_id=user.id,
            score=score,
        )

    async def check_user_lost(self, user: User):
        failures_count = await self.app.store.game.get_user_failures_count(
            game_id=self.id,
            user_id=user.id,
        )
        if failures_count == 3:
            await self.app.store.game.make_user_lost(
                game_id=self.id,
                user_id=user.id,
            )
            return True
        return False

    async def get_next_question(self) -> QuestionDC:
        await self._app.store.game.move_to_next_question(game_id=self.id)
        question = self._app.store.game.get_active_question(game_id=self.id)
        return question

    async def end(self):
        await self._app.store.game.end_game(peer_id=self.peer_id)

    async def get_winner(self) -> UserDC:
        winner = await self._app.store.game.get_winner_with_score(
            game_id=self.id,
        )
        return winner
