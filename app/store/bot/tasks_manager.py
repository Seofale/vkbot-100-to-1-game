import typing
import asyncio

from app.store.vk_api.dataclasses import Update
from app.store.bot.update_handler import UpdateHandler
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class UpdateTasksManager(BaseAccessor):
    def __init__(self, app: "Application"):
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
            if update.object.message:
                update_message = update.object.message
                task = asyncio.create_task(
                    self.update_handler.handle_message(
                        update_message=update_message
                    )
                )
            elif update.object.event:
                update_event = update.object.event
                task = asyncio.create_task(
                    self.update_handler.handle_event(
                        update_event=update_event
                    )
                )

            task.add_done_callback(self._log_task_exception)
            self.tasks.append(task)
