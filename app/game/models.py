import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.store.database.sqlalchemy_base import Base
from app.game.dataclasses import (
    UserDC, GameDC, QuestionDC, GameAnswerDC,
    AnswerDC, UserStatisticsDC, RoadmapDC
)


class GameModel(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True)
    peer_id: Mapped[int]
    started_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now()
    )
    ended_at: Mapped[datetime.datetime] = mapped_column(nullable=True)
    in_process: Mapped[bool] = mapped_column(default=True)
    roadmaps: Mapped[list["RoadmapModel"]] = relationship("RoadmapModel")

    def to_dataclass(self) -> GameDC:
        return GameDC(
            id=self.id,
            peer_id=self.peer_id,
            in_process=self.in_process,
            started_at=self.started_at,
            ended_at=self.ended_at
        )


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    vk_id: Mapped[int]
    first_name: Mapped[str] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str] = mapped_column(String(128), nullable=True)

    def to_dataclass(self) -> UserDC:
        return UserDC(
            id=self.id,
            vk_id=self.vk_id,
            first_name=self.first_name,
            last_name=self.last_name
        )


class StatisticsModel(Base):
    __tablename__ = "statistics"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_creator: Mapped[bool] = mapped_column(default=False)
    points: Mapped[int] = mapped_column(default=0)
    failures: Mapped[int] = mapped_column(default=0)
    is_lost: Mapped[bool] = mapped_column(default=False)
    is_winner: Mapped[bool] = mapped_column(default=False)

    def to_dataclass(self) -> UserStatisticsDC:
        return UserStatisticsDC(
            id=self.id,
            game_id=self.game_id,
            user_id=self.user_id,
            is_creator=self.is_creator,
            points=self.points,
            failures=self.failures,
            is_lost=self.is_lost,
            is_winner=self.is_winner
        )


class QuestionModel(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    answers: Mapped[list["AnswerModel"]] = relationship("AnswerModel")

    def to_dataclass(self) -> QuestionDC:
        return QuestionDC(
            id=self.id,
            title=self.title,
            answers=[answer.to_dataclass() for answer in self.answers]
        )


class AnswerModel(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    score: Mapped[int]

    def to_dataclass(self) -> AnswerDC:
        return AnswerDC(
            id=self.id,
            title=self.title,
            score=self.score,
            question_id=self.question_id
        )


class RoadmapModel(Base):
    __tablename__ = "roadmaps"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    status: Mapped[int]

    def to_dataclass(self) -> RoadmapDC:
        return RoadmapDC(
            id=self.id,
            game_id=self.game_id,
            question_id=self.question_id,
            status=self.status
        )


class GameAnswersModel(Base):
    __tablename__ = "game_answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"))

    def to_dataclass(self) -> GameAnswerDC:
        return GameAnswerDC(
            id=self.id,
            game_id=self.game_id,
            user_id=self.user_id,
            answer_id=self.answer_id
        )
