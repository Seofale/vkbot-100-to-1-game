import datetime
from dataclasses import dataclass


@dataclass
class UserDC:
    vk_id: int
    id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    score: int | None = None

    @property
    def full_name(self) -> str | None:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None


@dataclass
class UserStatisticsDC:
    id: int
    user_id: int
    game_id: int
    is_creator: bool
    points: int
    failures: int
    is_lost: bool
    is_winner: bool


@dataclass
class GameDC:
    id: int
    peer_id: int
    in_process: bool
    started_at: datetime.datetime
    ended_at: datetime.datetime | None = None


@dataclass
class QuestionDC:
    id: int
    title: str
    answers: list["AnswerDC"]


@dataclass
class AnswerDC:
    title: str
    score: int
    id: int | None = None
    question_id: int | None = None


@dataclass
class RoadmapDC:
    id: int
    game_id: int
    question_id: int
    status: int


@dataclass
class GameAnswerDC:
    id: int
    game_id: int
    user_id: int
    answer_id: int
