import asyncio
from logging import getLogger

from app.store import Store


class Poller:
    def __init__(self, store: Store):
        self.store = store
        self.is_running = False
        self.poll_task: asyncio.Task | None = None
        self.logger = getLogger("poller")

    async def start(self):
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())
        self.poll_task.add_done_callback(self._log_task_exception)

    async def stop(self):
        self.is_running = False
        await self.poll_task

    async def poll(self):
        while self.is_running:
            updates = await self.store.vk_api.poll()
            if updates:
                await self.store.tasks_manager.handle_updates(updates)

    def _log_task_exception(self, task: asyncio.Task):
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.warning(str(e))
