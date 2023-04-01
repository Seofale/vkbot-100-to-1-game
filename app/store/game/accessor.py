import datetime
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import func
from app.base.base_accessor import BaseAccessor
from app.game.models import (
    GameModel, UserModel, StatisticsModel,
    QuestionModel, RoadmapModel, AnswerModel,
    GameAnswersModel,
)
from app.game.dataclasses import (
    UserDC, GameDC, QuestionDC,
    AnswerDC, UserStatisticsDC, RoadmapDC
)
from app.store.utils import decorate_all_methods, add_db_session_to_accessor


@decorate_all_methods(add_db_session_to_accessor)
class GameAccessor(BaseAccessor):
    async def create_user(
        self,
        vk_id: int,
        **kwargs,
    ) -> UserDC:
        session = kwargs.get("session")
        user_data = await self.app.store.vk_api.get_user_info(
            vk_id=vk_id,
        )
        if user_data:
            user_model = UserModel(
                vk_id=vk_id,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
            )
        else:
            user_model = UserModel(
                vk_id=vk_id,
            )
        session.add(user_model)
        await session.commit()
        return user_model.to_dataclass()

    async def get_user(
        self,
        vk_id: int,
        **kwargs,
    ) -> UserDC | None:
        query = select(
            UserModel
        ).where(UserModel.vk_id == vk_id)
        session = kwargs.get("session")
        result = await session.execute(query)
        user_model = result.scalar()
        if user_model:
            return user_model.to_dataclass()
        return None

    async def get_user_statistics(
        self,
        game_id: int,
        user_id: int,
        **kwargs,
    ) -> UserStatisticsDC | None:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.game_id == game_id,
                StatisticsModel.user_id == user_id
            )
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        user_statistics_model = result.scalar()
        if user_statistics_model:
            return user_statistics_model.to_dataclass()
        return None

    async def get_winner_with_score(
        self,
        game_id: int,
        **kwargs,
    ) -> UserDC:
        query = select(
            UserModel
        ).where(
            StatisticsModel.game_id == game_id,
            StatisticsModel.is_lost == False  # noqa
        ).join(
            UserModel, StatisticsModel.user_id == UserModel.id
        ).add_columns(
            func.max(StatisticsModel.points)
        ).group_by(
            UserModel.id
        ).order_by(desc(func.max(StatisticsModel.points)))
        session = kwargs.get("session")
        result = await session.execute(query)
        user_model, score = result.first()
        user_statistics = await self.get_user_statistics(
            game_id=game_id,
            user_id=user_model.id
        )
        user_statistics.is_winner = True
        await session.merge(
            StatisticsModel(
                id=user_statistics.id,
                game_id=user_statistics.game_id,
                user_id=user_statistics.user_id,
                failures=user_statistics.failures,
                is_creator=user_statistics.is_creator,
                is_lost=user_statistics.is_lost,
                is_winner=user_statistics.is_winner
            )
        )
        await session.commit()
        return UserDC(
            id=user_model.id,
            vk_id=user_model.vk_id,
            score=score,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
        )

    async def get_users_count_in_game(
        self,
        game_id: int,
        **kwargs,
    ) -> int:
        query = select(
            func.count(StatisticsModel.id)
        ).where(
            StatisticsModel.game_id == game_id,
            StatisticsModel.is_lost == False  # noqa
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        return result.scalar()

    async def check_user_is_creator(
        self,
        game_id: int,
        user_id: int,
        **kwargs,
    ) -> bool:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.game_id == game_id,
                StatisticsModel.user_id == user_id
            )
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        user_statistics_model = result.scalar()
        if user_statistics_model:
            return user_statistics_model.is_creator
        return False

    async def create_game(
        self,
        peer_id: int,
        **kwargs,
    ) -> GameDC:
        session = kwargs.get("session")
        game_model = GameModel(peer_id=peer_id)
        session.add(game_model)

        three_random_questions_query = select(
            QuestionModel
        ).order_by(func.random()).limit(5)
        result = await session.execute(three_random_questions_query)
        questions = result.scalars()
        roadmaps = []
        for question in questions:
            roadmaps.append(RoadmapModel(
                game_id=game_model.id,
                question_id=question.id,
                status=0,
            ))

        roadmaps[0].status = 1

        session.add_all(roadmaps)
        await session.commit()

        return game_model.to_dataclass()

    async def get_game_by_peer_id(
        self,
        peer_id: int,
        **kwargs,
    ) -> GameDC | None:
        query = select(GameModel).where(
            and_(
                GameModel.peer_id == peer_id,
                GameModel.in_process == True,  # noqa
            )
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        game_model = result.scalar()
        if game_model:
            return game_model.to_dataclass()
        return None

    async def get_answer(
        self,
        title: str,
        question_id: int,
        **kwargs,
    ) -> AnswerDC | None:
        query = select(AnswerModel).where(
            and_(
                AnswerModel.title == title,
                AnswerModel.question_id == question_id
            )
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        answer_model = result.scalar()
        if answer_model:
            return answer_model.to_dataclass()
        return None

    async def create_game_answer(
        self,
        game_id: int,
        answer_id: int,
        user_id: int,
        **kwargs,
    ) -> None:
        session = kwargs.get("session")
        session.add(
            GameAnswersModel(
                game_id=game_id,
                answer_id=answer_id,
                user_id=user_id
            )
        )
        await session.commit()
        return None

    async def create_user_statistics(
        self,
        user_id: int,
        game_id: int,
        is_creator: bool = False,
        **kwargs,
    ) -> None:
        statistics_model = StatisticsModel(
            user_id=user_id,
            game_id=game_id,
            is_creator=is_creator
        )
        session = kwargs.get("session")
        session.add(statistics_model)
        await session.commit()

    async def add_points_to_user(
        self,
        game_id: int,
        user_id: int,
        score: int,
        **kwargs,
    ) -> None:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.user_id == user_id,
                StatisticsModel.game_id == game_id,
            )
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        statistics_model = result.scalar()
        statistics_model.points += score
        await session.merge(statistics_model)
        await session.commit()

    async def add_fail_to_user(
        self,
        game_id: int,
        user_id: int,
        **kwargs,
    ) -> None:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.user_id == user_id,
                StatisticsModel.game_id == game_id,
            )
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        statistics_model = result.scalar()
        statistics_model.failures += 1
        await session.merge(statistics_model)
        await session.commit()

    async def make_user_lost(
        self,
        game_id: int,
        user_id: int,
        **kwargs,
    ) -> None:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.user_id == user_id,
                StatisticsModel.game_id == game_id,
            )
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        statistics_model = result.scalar()
        statistics_model.is_lost = True
        await session.merge(statistics_model)
        await session.commit()

    async def get_user_failures_count(
        self,
        game_id: int,
        user_id: int,
        **kwargs,
    ) -> int:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.user_id == user_id,
                StatisticsModel.game_id == game_id,
            )
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        statistics_model = result.scalar()
        return statistics_model.failures

    async def end_game(
        self,
        peer_id: int,
        **kwargs,
    ) -> None:
        session = kwargs.get("session")
        game = await self.get_game_by_peer_id(
            peer_id=peer_id
        )
        game.ended_at = datetime.datetime.now()
        await session.merge(
            GameModel(
                id=game.id,
                started_at=game.started_at,
                ended_at=game.ended_at,
                peer_id=game.peer_id,
                in_process=False
            )
        )
        await session.commit()

    async def get_active_question(
        self,
        game_id: int,
        **kwargs,
    ) -> QuestionDC | None:
        query = select(
            QuestionModel
        ).options(
            selectinload(QuestionModel.answers)
        ).join(
            RoadmapModel,
            QuestionModel.id == RoadmapModel.question_id
        ).where(and_(
            RoadmapModel.status == 1,
            RoadmapModel.game_id == game_id
        ))
        session = kwargs.get("session")
        result = await session.execute(query)
        question_model = result.scalar()
        answers = []
        if question_model:
            for answer_model in question_model.answers:
                answers.append(
                    answer_model.to_dataclass()
                )
            return question_model.to_dataclass()
        return None

    async def move_to_next_question(
        self,
        game_id: int,
        **kwargs,
    ) -> bool:
        query = select(
            RoadmapModel
        ).where(
            RoadmapModel.game_id == game_id
        ).order_by(
            RoadmapModel.id
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        roadmap_models = result.scalars().all()
        for index in range(len(roadmap_models)):
            roadmap = roadmap_models[index]
            if roadmap.status == 1:
                roadmap.status = 0
                try:
                    next_roadmap = roadmap_models[index+1]
                    next_roadmap.status = 1
                except IndexError:
                    return False

                await session.merge(roadmap)
                await session.merge(next_roadmap)
                await session.commit()
                return True

    async def get_question_by_title(
        self,
        title: str,
        **kwargs,
    ) -> QuestionDC | None:
        query = select(
            QuestionModel
        ).options(
            selectinload(QuestionModel.answers)
        ).where(
            QuestionModel.title == title
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        question_model = result.scalar()
        if question_model:
            answers = []
            for answer_model in question_model.answers:
                answers.append(
                    answer_model.to_dataclass()
                )
            return question_model.to_dataclass()
        return None

    async def get_question_by_id(
        self,
        id: int,
        **kwargs,
    ) -> QuestionDC | None:
        query = select(
            QuestionModel
        ).options(
            selectinload(QuestionModel.answers)
        ).where(
            QuestionModel.id == id
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        question_model = result.scalar()
        if question_model:
            answers = []
            for answer_model in question_model.answers:
                answers.append(
                    answer_model.to_dataclass()
                )
            return question_model.to_dataclass()
        return None

    async def create_question(
        self,
        title: str,
        answers: list[AnswerDC],
        **kwargs,
    ) -> QuestionDC:
        session = kwargs.get("session")
        question_model = QuestionModel(
            title=title
        )
        answers_models = []
        for answer in answers:
            answer_model = AnswerModel(
                title=answer.title,
                question_id=question_model.id,
                score=answer.score
            )
            answers_models.append(answer_model)
        question_model.answers = answers_models
        session.add(question_model)
        await session.commit()

        response_answers = []
        for answer_model in question_model.answers:
            response_answers.append(
                answer_model.to_dataclass()
            )
        return question_model.to_dataclass()

    async def edit_question(
        self,
        id: int,
        title: str,
        answers: list[AnswerDC],
        **kwargs,
    ) -> QuestionDC:
        query = select(
            QuestionModel
        ).options(
            selectinload(QuestionModel.answers)
        ).where(
            QuestionModel.id == id
        )
        session = kwargs.get("session")
        result = await session.execute(query)
        question_model = result.scalar()
        if question_model:
            for answer in answers:
                answer_model = AnswerModel(
                    id=answer.id,
                    title=answer.title,
                    question_id=question_model.id,
                    score=answer.score
                )
                await session.merge(answer_model)
            question_model.title = title
            question_model = await session.merge(question_model)
            await session.commit()
            return question_model.to_dataclass()

    async def list_questions(
        self,
        page: int | None,
        offset: int = 5,
        game_id: int | None = None,
        **kwargs,
    ) -> list[QuestionDC]:
        query = select(
            QuestionModel
        ).options(
            selectinload(QuestionModel.answers)
        )
        if game_id:
            query = query.join(
                RoadmapModel, QuestionModel.id == RoadmapModel.question_id
            ).where(
                RoadmapModel.game_id == game_id
            )
        if page:
            query = query.limit(offset).offset(offset * (page - 1))

        session = kwargs.get("session")
        result = await session.execute(query)
        question_models = result.scalars()
        questions = []
        for question_model in question_models:
            answers = []
            for answer_model in question_model.answers:
                answers.append(
                    answer_model.to_dataclass()
                )
            questions.append(
                QuestionDC(
                    id=question_model.id,
                    title=question_model.title,
                    answers=answers
                )
            )
        return questions

    async def list_games(
        self,
        page: int | None,
        offset: int = 5,
        peer_id: int | None = None,
        **kwargs,
    ) -> list[GameDC]:
        query = select(
            GameModel
        )
        if peer_id:
            query = query.where(
                GameModel.peer_id == peer_id
            )
        if page:
            query = query.limit(offset).offset(offset * (page - 1))
        session = kwargs.get("session")
        result = await session.execute(query)
        game_models = result.scalars()
        games = []
        for game_model in game_models:
            games.append(
                game_model.to_dataclass()
            )
        return games

    async def list_users(
        self,
        page: int | None,
        offset: int = 5,
        game_id: int | None = None,
        **kwargs,
    ) -> list[UserDC]:
        query = select(
            UserModel
        )
        if game_id:
            query = query.join(
                StatisticsModel, UserModel.id == StatisticsModel.user_id
            ).where(
                StatisticsModel.game_id == game_id
            )
        if page:
            query = query.limit(offset).offset(offset * (page - 1))
        session = kwargs.get("session")
        result = await session.execute(query)
        user_models = result.scalars()
        users = []
        for user_model in user_models:
            users.append(
                user_model.to_dataclass()
            )
        return users

    async def list_roadmaps(
        self,
        page: int | None,
        offset: int = 5,
        game_id: int | None = None,
        **kwargs,
    ) -> list[RoadmapDC]:
        query = select(
            RoadmapModel
        )
        if game_id:
            query = query.where(
                RoadmapModel.game_id == game_id
            )
        if page:
            query = query.limit(offset).offset(offset * (page - 1))
        session = kwargs.get("session")
        result = await session.execute(query)
        roadmap_models = result.scalars()
        roadmaps = []
        for roadmap_model in roadmap_models:
            roadmaps.append(
                roadmap_model.to_dataclass()
            )
        return roadmaps

    async def list_user_statistics(
        self,
        page: int | None,
        offset: int = 5,
        game_id: int | None = None,
        user_id: int | None = None,
        **kwargs,
    ) -> list[UserStatisticsDC]:
        query = select(
            StatisticsModel
        )
        if game_id or user_id:
            if game_id and user_id:
                query = query.where(
                    and_(
                        StatisticsModel.game_id == game_id,
                        StatisticsModel.user_id == user_id
                    )
                )
            elif game_id:
                query = query.where(
                    StatisticsModel.game_id == game_id
                )
            elif user_id:
                query = query.where(
                    StatisticsModel.user_id == user_id
                )
        if page:
            query = query.limit(offset).offset(offset * (page - 1))
        session = kwargs.get("session")
        result = await session.execute(query)
        user_statistics_models = result.scalars()
        user_statistics = []
        for user_statistics_model in user_statistics_models:
            user_statistics.append(
                user_statistics_model.to_dataclass()
            )
        return user_statistics
