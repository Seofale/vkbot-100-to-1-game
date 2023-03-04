import datetime
from dataclasses import dataclass


@dataclass
class User:
    id: int
    vk_id: int


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
