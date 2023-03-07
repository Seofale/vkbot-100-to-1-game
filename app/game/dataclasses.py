import datetime
from dataclasses import dataclass


@dataclass
class User:
    id: int
    vk_id: int
    score: int | None = None


@dataclass
class UserStatistics:
    id: int
    user_id: int
    game_id: int
    is_creator: bool
    points: int
    failures: int
    is_lost: bool


@dataclass
class Game:
    id: int
    peer_id: int
    started_at: datetime.datetime
    ended_at: datetime.datetime | None = None


@dataclass
class Question:
    id: int
    title: str
    answers: list["Answer"]


@dataclass
class Answer:
    id: int
    title: str
    question_id: int
    score: int
