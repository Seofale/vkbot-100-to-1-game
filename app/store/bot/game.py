import typing
if typing.TYPE_CHECKING:
    from app.web.app import Application


class Game:
    def __init__(self, app: "Application", peer_id: int):
        self.app = app
        self.peer_id = peer_id
        self.is_created = False

    async def create(self, peer_id: int):
        await self.app.store.game.create_game(
            peer_id=peer_id,
        )
        self.is_created = True
