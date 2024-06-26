import random
import typing
import json

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor

from app.store.bot.updates import UpdateEvent, UpdateMessage

from app.game.dataclasses import UserDC
from app.store.vk_api.poller import Poller
from app.store.bot.keyboards import Keyboard

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

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
                upd_obj = update["object"]
                if upd_obj.get("message"):
                    message = upd_obj.get("message")
                    updates.append(
                        UpdateMessage(
                            app=self.app,
                            user_id=message["from_id"],
                            text=message["text"],
                            peer_id=message["peer_id"],
                            event_id=update["event_id"],
                            cmd=message["conversation_message_id"],
                        )
                    )
                elif upd_obj.get("event_id"):
                    updates.append(
                        UpdateEvent(
                            app=self.app,
                            user_id=upd_obj["user_id"],
                            peer_id=upd_obj["peer_id"],
                            event_id=upd_obj["event_id"],
                            payload=upd_obj["payload"],
                        )
                    )
            await self.app.store.tasks_manager.handle_updates(updates=updates)

    async def send_message(
        self,
        peer_id: int,
        text: str,
        keyboard: Keyboard,
    ) -> int:
        """
        return conversation_message_id which helps to edit and delete messages
        """
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.send",
                params={
                    "random_id": random.randint(1, 2**32),
                    "peer_ids": peer_id,
                    "message": text,
                    "access_token": self.app.config.bot.token,
                    "keyboard": json.dumps(keyboard.to_dict())
                    if keyboard != "" else "",
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)
            if data.get("error"):
                self.logger.error(msg=data["error"]["error_msg"])
                return None
            cmd = data["response"][0]["conversation_message_id"]
            return cmd

    async def edit_message(
        self,
        peer_id: int,
        text: str,
        cmd: int,
    ):
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.edit",
                params={
                    "conversation_message_id": cmd,
                    "peer_id": peer_id,
                    "message": text,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def show_snackbar(
        self,
        event_id: int,
        user_id: int,
        peer_id: int,
        text: str,
    ):
        async with self.session.get(
            self._build_query(
                API_PATH,
                "messages.sendMessageEventAnswer",
                params={
                    "event_id": event_id,
                    "user_id": user_id,
                    "peer_id": peer_id,
                    "access_token": self.app.config.bot.token,
                    "event_data": json.dumps({
                        "type": "show_snackbar",
                        "text": text,
                    })
                },
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def get_user_info(self, vk_id: int):
        async with self.session.get(
            self._build_query(
                API_PATH,
                "users.get",
                params={
                    "access_token": self.app.config.bot.token,
                    "user_ids": vk_id,
                },
            )
        ) as resp:
            data = await resp.json()
            if data.get("error"):
                self.logger.error(msg=data["error"]["error_msg"])
                return None
            self.logger.info(data)
            user_data = data["response"][0]
            return UserDC(
                vk_id=vk_id,
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
            )
