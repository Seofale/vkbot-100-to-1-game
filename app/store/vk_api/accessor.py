import random
import typing
import json
from typing import Optional

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import (
    Message, Update, UpdateObject, UpdateMessage,
    UpdateAction, UpdateEvent
)
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)
        self.poller = Poller(app.store)
        self.logger.info("start polling")
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = (await resp.json())["response"]
            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(self.server)

    async def poll(self):
        async with self.session.get(
            self._build_query(
                host=self.server,
                method="",
                params={
                    "act": "a_check",
                    "key": self.key,
                    "ts": self.ts,
                    "wait": 30,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
            self.ts = data["ts"]
            raw_updates = data.get("updates", [])
            updates = []
            for update in raw_updates:
                updates.append(
                    Update(
                        type=update["type"],
                        object=UpdateObject(
                            message=UpdateMessage(
                                id=update["object"]["message"]["id"],
                                from_id=update["object"]["message"]["from_id"],
                                text=update["object"]["message"]["text"],
                                peer_id=update["object"]["message"]["peer_id"],
                            ) if update["object"].get("message") else None,
                            action=UpdateAction(
                                type=update["object"]["message"]["action"]["type"],
                                peer_id=update["object"]["message"]["peer_id"],
                            ) if update["object"].get("message", {}).get("action") else None,
                            event=UpdateEvent(
                                user_id=update["object"]["user_id"],
                                peer_id=update["object"]["peer_id"],
                                event_id=update["object"]["event_id"],
                                payload=update["object"]["payload"],
                            ) if update["object"].get("event_id") else None
                        ),
                    )
                )
            await self.app.store.bots_manager.handle_updates(updates=updates)

    async def send_message(self, message: Message):
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "random_id": random.randint(1, 2**32),
                    "peer_id": message.peer_id,
                    "message": message.text,
                    "access_token": self.app.config.bot.token,
                    "keyboard": message.keyboard
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def show_snackbar_event_answer(
        self,
        update_event: UpdateEvent,
        text: str
    ):
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.sendMessageEventAnswer",
                params={
                    "event_id": update_event.event_id,
                    "user_id": update_event.user_id,
                    "peer_id": update_event.peer_id,
                    "access_token": self.app.config.bot.token,
                    "event_data": json.dumps({
                        "type": "show_snackbar",
                        "text": text
                    })
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
