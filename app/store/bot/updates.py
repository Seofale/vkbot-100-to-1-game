import typing

from app.store.bot.game import Game

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Update:
    def __init__(
        self,
        app: "Application",
        peer_id: int,
        user_id: int,
        event_id: int,
    ):
        self.app = app
        self.peer_id = peer_id
        self.user_id = user_id
        self.event_id = event_id
        self.game = Game(
            app=app,
            peer_id=peer_id,
        )


class UpdateMessage:
    def __init__(
        self,
        app: "Application",
        peer_id: int,
        user_id: int,
        event_id: int,
        text: str,
        cmd: int,
    ):
        super().__init__(
            app=app,
            peer_id=peer_id,
            user_id=user_id,
            event_id=event_id,
        )
        self.text = text
        self.cmd = cmd


class UpdateEvent:
    def __init__(
        self,
        app: "Application",
        peer_id: int,
        user_id: int,
        event_id: int,
        payload: str,
    ):
        super().__init__(
            app=app,
            peer_id=peer_id,
            user_id=user_id,
            event_id=event_id,
        )
        self.payload = payload
