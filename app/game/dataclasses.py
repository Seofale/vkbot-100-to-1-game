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
    in_process: bool
    started_at: datetime.datetime
    ended_at: datetime.datetime | None = None


@dataclass
class Question:
    id: int
    title: str
    answers: list["Answer"]


@dataclass
class Answer:
    title: str
    score: int
    id: int | None = None
    question_id: int | None = None


@dataclass
class Roadmap:
    id: int
    game_id: int
    question_id: int
    status: int


@dataclass
class GameAnswer:
    id: int
    game_id: int
    user_id: int
    answer_id: int
