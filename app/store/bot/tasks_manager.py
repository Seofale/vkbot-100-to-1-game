import typing
import asyncio

from app.store.bot.update_handler import UpdateHandler
from app.base.base_accessor import BaseAccessor
from app.store.bot.updates import UpdateEvent, UpdateMessage, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class UpdateTasksManager(BaseAccessor):
    def __init__(self, app: "Application"):
        self.app = app
        self.update_handler = UpdateHandler(app)
        self.tasks: list[asyncio.Task] = []
        self.clear_task: asyncio.Task = None
        self.is_running = False
        super().__init__(app)

    async def connect(self, app):
        self.is_running = True
        self.logger.info("start tasks manager")
        self.clear_task = asyncio.create_task(self.clear_tasks())
        self.clear_task.add_done_callback(self._log_task_exception)

    async def disconnect(self, app):
        self.is_running = False
        self.logger.info("start shutting down tasks manager")
        await self.clear_task
        for task in self.tasks:
            if task.done() or task.cancelled():
                continue
            await task

    async def clear_tasks(self):
        while self.is_running:
            await asyncio.sleep(10)
            self.tasks = [task for task in self.tasks if not (
                task.done() or task.cancelled())]

    def _log_task_exception(self, task: asyncio.Task):
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        # except Exception as e:
        #     self.logger.warning(str(e))

    async def handle_updates(self, updates: list[Update]) -> None:
        for update in updates:
            if isinstance(update, UpdateMessage):
                update_message = update
                task = asyncio.create_task(
                    self.update_handler.handle_message(
                        upd_msg=update_message
                    )
                )
            elif isinstance(update, UpdateEvent):
                update_event = update
                task = asyncio.create_task(
                    self.update_handler.handle_event(
                        upd_event=update_event
                    )
                )

            task.add_done_callback(self._log_task_exception)
            self.tasks.append(task)
