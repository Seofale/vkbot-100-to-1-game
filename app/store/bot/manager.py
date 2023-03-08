import typing
import json
from logging import getLogger

from app.store.vk_api.dataclasses import (
    Message, Update, UpdateEvent, UpdateMessage
)
from app.game.dataclasses import Game
from app.store.bot.enums import ActionTypesEnum, BotCommandsEnum
from app.store.bot.keyboards import (
    start_keyboard, create_keyboard, end_keyboard
)

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
                if update.object.action.type == ActionTypesEnum \
                        .user_joined_chat.value:
                    await self.app.store.vk_api.send_message(
                        Message(
                            peer_id=update.object.message.peer_id,
                            keyboard=json.dumps(
                                create_keyboard.to_dict()
                            ),
                            text="Привет! Теперь вам доступна клавиатура бота",
                        )
                    )

            elif update.object.event:
                event = update.object.event

                match update.object.event.payload["command"]:
                    case BotCommandsEnum.create_game.value:
                        await self.create_game(event=event)

                    case BotCommandsEnum.end_game.value:
                        await self.end_game(event=event)

                    case BotCommandsEnum.user_joined_game.value:
                        await self.join_game(event=event)

                    case BotCommandsEnum.start_game.value:
                        await self.start_game(event=event)

            elif update.object.message:
                message = update.object.message
                await self.handle_answer(message=message)

    async def create_game(self, event: UpdateEvent) -> None:
        game = await self.app.store.game.get_game_by_peer_id(
            peer_id=event.peer_id
        )
        if game:
            await self.app.store.vk_api.show_snackbar_event_answer(
                update_event=event,
                text="В этом чате уже создана игра"
            )
            return

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
                keyboard=json.dumps(start_keyboard.to_dict()),
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
                keyboard=json.dumps(start_keyboard.to_dict())
            )
        )

    async def join_game(self, event: UpdateEvent) -> None:
        game = await self.app.store.game.get_game_by_peer_id(
            peer_id=event.peer_id
        )
        user = await self.app.store.game.get_user(vk_id=event.user_id)
        if not user:
            user = await self.app.store.game.create_user(vk_id=event.user_id)

        user_in_game = await self.app.store.game.check_user_in_game(
            user_id=user.id,
            game_id=game.id
        )

        if user_in_game:
            await self.app.store.vk_api.show_snackbar_event_answer(
                update_event=event,
                text="Вы уже присоединились к этой игре"
            )
            return

        await self.app.store.game.create_user_statistics(
            user_id=user.id,
            game_id=game.id
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
        game = await self.app.store.game.get_game_by_peer_id(
            peer_id=event.peer_id
        )
        if not game:
            return

        user = await self.app.store.game.get_user(vk_id=event.user_id)
        if not user:
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
                keyboard=json.dumps(end_keyboard.to_dict())
            )
        )

    async def handle_answer(self, message: UpdateMessage) -> None:
        game = await self.app.store.game.get_game_by_peer_id(
            peer_id=message.peer_id
        )
        if not game:
            return

        user = await self.app.store.game.get_user(
            vk_id=message.from_id
        )
        if not user:
            return

        user_statistics = await self.app.store.game.get_user_statistics(
            user_id=user.id,
            game_id=game.id
        )
        if not user_statistics:
            return
        if user_statistics.is_lost:
            return

        active_question = await self.app.store.game \
            .get_question_in_active_roadmap(
                game_id=game.id
            )
        answer = await self.app.store.game.get_answer_by_title_and_question_id(
            title=message.text.lower(),
            question_id=active_question.id
        )
        if not answer:
            await self.app.store.game.add_fail_to_user(
                game_id=game.id,
                user_id=user.id
            )

            user_failures_count = await self.app.store.game \
                .get_user_failures_count(
                    game_id=game.id,
                    user_id=user.id
                )
            if user_failures_count == 3:
                await self.app.store.game.make_user_lost(
                    game_id=game.id,
                    user_id=user.id
                )
                await self.app.store.vk_api.send_message(
                    Message(
                        peer_id=message.peer_id,
                        text=f"@id{user.vk_id} \
                            исчерпал все свои попытки и выбыл из игры",
                    )
                )
            await self.app.store.vk_api.send_message(
                Message(
                    peer_id=message.peer_id,
                    text=f"@id{user.vk_id} \
                            первым ответил на вопрос, но оказался неправ :(",
                )
            )

            await self.send_next_question_or_end_game(game=game)

            return

        await self.app.store.vk_api.send_message(
            Message(
                peer_id=message.peer_id,
                text=f"@id{user.vk_id} \
                            получил {answer.score} очков за свой ответ",
            )
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

        await self.send_next_question_or_end_game(game=game)

    async def send_next_question_or_end_game(self, game: Game) -> None:
        next_question_exists = await self.app.store.game.move_to_next_question(
            game_id=game.id
        )
        if not next_question_exists:
            winner = await self.app.store.game.get_winner_with_score(
                game_id=game.id
            )
            await self.app.store.vk_api.send_message(
                Message(
                    peer_id=game.peer_id,
                    text=f"Игра окончена. Победитель: @id{winner.vk_id}, \
                        количество очков: {winner.score}",
                    keyboard=json.dumps(end_keyboard.to_dict())
                )
            )
            await self.app.store.game.end_game(peer_id=game.peer_id)
            return

        active_question = await self.app.store.game \
            .get_question_in_active_roadmap(
                game_id=game.id
            )
        await self.app.store.vk_api.send_message(
            Message(
                peer_id=game.peer_id,
                text=active_question.title
            )
        )
