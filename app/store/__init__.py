import typing

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.bot.manager import BotManager
        from app.store.vk_api.accessor import VkApiAccessor
        from app.store.game.accessor import GameAccessor
        from app.store.admin.accessor import AdminAccessor

        self.vk_api = VkApiAccessor(app)
        self.bot_manager = BotManager(app)
        self.game = GameAccessor(app)
        self.admins = AdminAccessor(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.store = Store(app)
    app.on_cleanup.append(app.database.disconnect)
