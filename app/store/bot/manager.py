import typing
import json
from logging import getLogger

from app.store.vk_api.dataclasses import Message, Update, UpdateEvent
from app.game.dataclasses import Game, User
from app.store.bot import constants
from app.store.bot.utils import get_answers_keyboard

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.bot = None
        self.logger = getLogger("handler")

    async def handle_updates(self, updates: list[Update]) -> None:
        for update in updates:
            if update.object.action:
                if update.object.action.type == "chat_invite_user":
                    await self.app.store.vk_api.send_message(
                        Message(
                            peer_id=update.object.message.peer_id,
                            keyboard=json.dumps(
                                constants.CREATE_GAME_KEYBOARD
                            ),
                            text=".",
                        )
                    )
            if update.object.event:
                if update.object.event.payload["command"] == "create":
                    await self.create_game(event=update.object.event)

                if update.object.event.payload["command"] == "end":
                    await self.end_game(event=update.object.event)

                if update.object.event.payload["command"] == "join":
                    await self.join_game(event=update.object.event)

                if update.object.event.payload["command"] == "start":
                    await self.start_game(event=update.object.event)

                if update.object.event.payload["command"] == "answer":
                    await self.answer_handler(event=update.object.event)

    async def create_game(self, event: UpdateEvent) -> None:
        game = await self.app.store.game.create_game(peer_id=event.peer_id)
        user = await self.app.store.game.get_user(vk_id=event.user_id)
        if not user:
            user = await self.app.store.game.create_user(vk_id=event.user_id)

        await self.app.store.game.create_user_statistics(
            user_id=user.id,
            game_id=game.id,
            is_creator=True
        )

        await self.app.store.vk_api.show_snackbar_event_answer(
            update_event=event,
            text="Игра создана, ожидаем игроков"
        )

        await self.app.store.vk_api.send_message(
            Message(
                peer_id=event.peer_id,
                keyboard=json.dumps(constants.START_GAME_KEYBOARD),
                text=f"Только что @id{event.user_id} создал игру"
            )
        )

    async def end_game(self, event: UpdateEvent) -> None:
        await self.app.store.game.end_game(peer_id=event.peer_id)

        await self.app.store.vk_api.show_snackbar_event_answer(
            update_event=event,
            text="Игра окончена"
        )

        await self.app.store.vk_api.send_message(
            Message(
                peer_id=event.peer_id,
                text=f"Только что @id{event.user_id} закончил игру",
                keyboard=json.dumps(constants.CREATE_GAME_KEYBOARD)
            )
        )

    async def join_game(self, event: UpdateEvent) -> None:
        game = await self.app.store.game.get_game_by_peer_id(
            peer_id=event.peer_id
        )
        user = await self.app.store.game.get_user(vk_id=event.user_id)
        if not user:
            user = await self.app.store.game.create_user(vk_id=event.user_id)

        await self.app.store.game.create_user_statistics(
            user_id=user.id,
            game_id=game.id
        )

        user_in_game = await self.app.store.game.check_user_in_game(
            user_id=user.id,
            game_id=game.id
        )

        if user_in_game:
            await self.app.store.vk_api.show_snackbar_event_answer(
                update_event=event,
                text="Вы уже присоединились к этой игре"
            )

        await self.app.store.vk_api.show_snackbar_event_answer(
            update_event=event,
            text="Вы присоединились к игре"
        )
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=event.peer_id,
                text=f"@id{event.user_id} присоединился к игре",
            )
        )

    async def start_game(self, event: UpdateEvent) -> None:
        game, user = await self.get_game_and_user_if_user_in_game(event=event)
        if not game:
            return

        if not (await self.app.store.game.check_user_is_creator(
            user_id=user.id,
            game_id=game.id
        )):
            await self.app.store.vk_api.show_snackbar_event_answer(
                update_event=event,
                text="Только создатель игры может её начать"
            )
            return

        await self.app.store.vk_api.show_snackbar_event_answer(
            update_event=event,
            text="Вы начали игру"
        )

        question = await self.app.store.game.get_question_in_active_roadmap(
            game_id=game.id
        )
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=event.peer_id,
                text=question.title,
                keyboard=get_answers_keyboard(question.answers)
            )
        )

    async def answer_handler(self, event: UpdateEvent) -> None:
        game, user = await self.get_game_and_user_if_user_in_game(event=event)
        active_question = await self.app.store.game.get_question_in_active_roadmap(
            game_id=game.id
        )
        answer = await self.app.store.game.get_answer_by_title_and_question_id(
            title=event.payload["answer"],
            question_id=active_question.id
        )
        await self.app.store.game.add_points_to_user(
            user_id=user.id,
            game_id=game.id,
            score=answer.score
        )
        await self.app.store.game.create_game_answer(
            game_id=game.id,
            answer_id=answer.id,
            user_id=user.id
        )
        next_question_exists = await self.app.store.game.move_to_next_question(
            game_id=game.id
        )
        if not next_question_exists:
            winner_vk_id, points = await self.app.store.game.get_winner_id_and_points(
                game_id=game.id
            )
            await self.app.store.vk_api.send_message(
                Message(
                    peer_id=event.peer_id,
                    text=f"Игра окончена. Победитель: @id{winner_vk_id}, количество очков: {points}",
                    keyboard=json.dumps(constants.CREATE_GAME_KEYBOARD)
                )
            )
            await self.app.store.game.end_game(peer_id=event.peer_id)

            await self.app.store.vk_api.show_snackbar_event_answer(
                update_event=event,
                text="Игра окончена"
            )
            return

        await self.app.store.vk_api.show_snackbar_event_answer(
            update_event=event,
            text="Вы выбрали ответ"
        )
        active_question = await self.app.store.game.get_question_in_active_roadmap(
            game_id=game.id
        )
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=event.peer_id,
                text=active_question.title,
                keyboard=get_answers_keyboard(active_question.answers)
            )
        )

    async def get_game_and_user_if_user_in_game(
        self,
        event: UpdateEvent
    ) -> (Game, User):
        game = await self.app.store.game.get_game_by_peer_id(
            peer_id=event.peer_id
        )
        user = await self.app.store.game.get_user(vk_id=event.user_id)
        if not user:
            await self.app.store.vk_api.show_snackbar_event_answer(
                update_event=event,
                text="Пока вы не участвовали ни в одной игре :("
            )
            return (None, None)

        if not game:
            await self.app.store.vk_api.show_snackbar_event_answer(
                update_event=event,
                text="Вы не можете присоединиться к игре, так как она не создана в этом чате :("
            )
            return (None, None)

        user_in_game = await self.app.store.game.check_user_in_game(
            user_id=user.id,
            game_id=game.id
        )

        if not user_in_game:
            await self.app.store.vk_api.show_snackbar_event_answer(
                update_event=event,
                text="Вы не присоединились к этой игре"
            )
            return (None, None)

        return (game, user)
