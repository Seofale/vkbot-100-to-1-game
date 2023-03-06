import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.store.database.sqlalchemy_base import Base


class GameModel(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True)
    peer_id: Mapped[int]
    started_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now()
    )
    ended_at: Mapped[datetime.datetime] = mapped_column(nullable=True)
    roadmaps: Mapped[list["RoadmapModel"]] = relationship("RoadmapModel")


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    vk_id: Mapped[int]


class StatisticsModel(Base):
    __tablename__ = "statistics"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_creator: Mapped[bool] = mapped_column(default=False)
    points: Mapped[int] = mapped_column(default=0)
    failures: Mapped[int] = mapped_column(default=0)
    is_lost: Mapped[bool] = mapped_column(default=False, nullable=True)


class QuestionModel(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    answers: Mapped[list["AnswerModel"]] = relationship("AnswerModel")


class AnswerModel(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    score: Mapped[int]


class RoadmapModel(Base):
    __tablename__ = "roadmaps"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    status: Mapped[int]


class GameAnswersModel(Base):
    __tablename__ = "game_answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"))
