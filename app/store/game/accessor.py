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
    User, Game, Question, Answer, UserStatistics
)


class GameAccessor(BaseAccessor):
    async def create_user(self, vk_id: int) -> User:
        async with self.app.database.session() as session:
            user_model = UserModel(vk_id=vk_id)
            session.add(user_model)
            await session.commit()
            return User(
                id=user_model.id,
                vk_id=user_model.vk_id,
            )

    async def get_user(self, vk_id: int) -> User | None:
        query = select(
            UserModel
        ).where(UserModel.vk_id == vk_id)
        async with self.app.database.session() as session:
            result = await session.execute(query)
            user_model = result.scalar()
            if user_model:
                return User(
                    id=user_model.id,
                    vk_id=user_model.vk_id
                )
            return None

    async def get_user_statistics(self, game_id: int, user_id: int) -> bool:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.game_id == game_id,
                StatisticsModel.user_id == user_id
            )
        )
        async with self.app.database.session() as session:
            result = await session.execute(query)
            user_statistics_model = result.scalar()
            if user_statistics_model:
                return UserStatistics(
                    id=user_statistics_model.id,
                    user_id=user_statistics_model.user_id,
                    game_id=user_statistics_model.game_id,
                    is_creator=user_statistics_model.is_creator,
                    points=user_statistics_model.points,
                    failures=user_statistics_model.failures,
                    is_lost=user_statistics_model.is_lost
                )
            return None

    async def get_winner_with_score(self, game_id: int) -> User:
        query = select(
            UserModel
        ).where(
            StatisticsModel.game_id == game_id
        ).join(
            UserModel, StatisticsModel.user_id == UserModel.id
        ).add_columns(
            func.max(StatisticsModel.points)
        ).group_by(
            UserModel.id
        ).order_by(desc(func.max(StatisticsModel.points)))

        async with self.app.database.session() as session:
            result = await session.execute(query)
            user_model, score = result.first()
            return User(
                id=user_model.id,
                vk_id=user_model.vk_id,
                score=score
            )

    async def check_user_is_creator(self, game_id: int, user_id: int) -> bool:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.game_id == game_id,
                StatisticsModel.user_id == user_id
            )
        )
        async with self.app.database.session() as session:
            result = await session.execute(query)
            user_statistics_model = result.scalar()
            return user_statistics_model.is_creator

    async def create_game(self, peer_id: int) -> Game:
        async with self.app.database.session() as session:
            game_model = GameModel(peer_id=peer_id)
            session.add(game_model)

            three_random_questions_query = select(
                QuestionModel
            ).order_by(func.random()).limit(3)
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

            return Game(
                id=game_model.id,
                peer_id=game_model.peer_id,
                started_at=game_model.started_at,
                ended_at=game_model.ended_at
            )

    async def get_game_by_peer_id(self, peer_id: int) -> Game | None:
        query = select(GameModel).where(
            and_(
                GameModel.peer_id == peer_id,
                GameModel.ended_at == None,
            )
        )
        async with self.app.database.session() as session:
            result = await session.execute(query)
            game_model = result.scalar()
            if game_model:
                return Game(
                    id=game_model.id,
                    peer_id=game_model.peer_id,
                    started_at=game_model.started_at,
                    ended_at=game_model.ended_at
                )
            return None

    async def get_answer_by_title_and_question_id(
        self,
        title: str,
        question_id: int
    ) -> Answer | None:
        query = select(AnswerModel).where(
            and_(
                AnswerModel.title == title,
                AnswerModel.question_id == question_id
            )
        )
        async with self.app.database.session() as session:
            result = await session.execute(query)
            answer_model = result.scalar()
            if answer_model:
                return Answer(
                    id=answer_model.id,
                    title=answer_model.title.lower(),
                    question_id=answer_model.question_id,
                    score=answer_model.score
                )
            return None

    async def create_game_answer(
        self,
        game_id: int,
        answer_id: int,
        user_id: int
    ) -> None:
        async with self.app.database.session() as session:
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
        is_creator: bool = False
    ) -> None:
        async with self.app.database.session() as session:
            statistics_model = StatisticsModel(
                user_id=user_id,
                game_id=game_id,
                is_creator=is_creator
            )
            session.add(statistics_model)
            await session.commit()

    async def add_points_to_user(
        self,
        game_id: int,
        user_id: int,
        score: int
    ) -> None:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.user_id == user_id,
                StatisticsModel.game_id == game_id,
            )
        )
        async with self.app.database.session() as session:
            result = await session.execute(query)
            statistics_model = result.scalar()
            statistics_model.points += score
            await session.merge(statistics_model)
            await session.commit()

    async def add_fail_to_user(self, game_id: int, user_id: int) -> None:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.user_id == user_id,
                StatisticsModel.game_id == game_id,
            )
        )
        async with self.app.database.session() as session:
            result = await session.execute(query)
            statistics_model = result.scalar()
            statistics_model.failures += 1
            await session.merge(statistics_model)
            await session.commit()

    async def make_user_lost(self, game_id: int, user_id: int) -> None:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.user_id == user_id,
                StatisticsModel.game_id == game_id,
            )
        )
        async with self.app.database.session() as session:
            result = await session.execute(query)
            statistics_model = result.scalar()
            statistics_model.is_lost = True
            await session.merge(statistics_model)
            await session.commit()

    async def get_user_failures_count(self, game_id: int, user_id: int) -> int:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.user_id == user_id,
                StatisticsModel.game_id == game_id,
            )
        )
        async with self.app.database.session() as session:
            result = await session.execute(query)
            statistics_model = result.scalar()
            return statistics_model.failures

    async def check_user_in_game(self, user_id: int, game_id: int) -> bool:
        query = select(StatisticsModel).where(
            and_(
                StatisticsModel.user_id == user_id,
                StatisticsModel.game_id == game_id,
            )
        )
        async with self.app.database.session() as session:
            result = await session.execute(query)
            statistics_model = result.scalar()
            if statistics_model:
                return True
            return False

    async def end_game(self, peer_id: int) -> None:
        game = await self.get_game_by_peer_id(
            peer_id=peer_id
        )
        game.ended_at = datetime.datetime.now()
        async with self.app.database.session() as session:
            await session.merge(GameModel(
                id=game.id,
                started_at=game.started_at,
                ended_at=game.ended_at,
                peer_id=game.peer_id
            ))
            await session.commit()

    async def get_question_in_active_roadmap(
        self,
        game_id: int
    ) -> Question | None:
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
        async with self.app.database.session() as session:
            result = await session.execute(query)
            question_model = result.scalar()
            answers = []
            if question_model:
                for answer_model in question_model.answers:
                    answers.append(
                        Answer(
                            id=answer_model.id,
                            title=answer_model.title,
                            question_id=answer_model.question_id,
                            score=answer_model.score
                        )
                    )
                return Question(
                    id=question_model.id,
                    title=question_model.title,
                    answers=answers
                )
            return None

    async def move_to_next_question(self, game_id: int) -> bool:
        query = select(
            RoadmapModel
        ).where(
            RoadmapModel.game_id == game_id
        ).order_by(
            RoadmapModel.id
        )
        async with self.app.database.session() as session:
            result = await session.execute(query)
            roadmap_models = result.scalars().all()
            for index in range(len(roadmap_models)):
                self.logger.info(index)
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
