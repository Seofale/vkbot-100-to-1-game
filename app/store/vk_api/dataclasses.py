from dataclasses import dataclass

from app.store.bot.keyboards import Keyboard


@dataclass
class Message:
    peer_id: int
    text: str
    keyboard: Keyboard | str = ""


@dataclass
class UpdateMessage:
    id: int
    from_id: int
    text: str
    peer_id: int
    conversation_message_id: int


@dataclass
class UpdateAction:
    type: str
    peer_id: int


@dataclass
class UpdateEvent:
    user_id: int
    peer_id: int
    event_id: int
    payload: str


@dataclass
class UpdateObject:
    message: UpdateMessage | None
    action: UpdateAction | None
    event: UpdateEvent | None


@dataclass
class Update:
    type: str
    object: UpdateObject
