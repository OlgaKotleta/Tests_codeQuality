import json
import logging
import time

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s.%(msecs)03d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Dispatcher:
    def __init__(self, storage: Storage, messenger: Messenger) -> None:
        self._handlers: list[Handler] = []
        self._storage: Storage = storage
        self._messenger: Messenger = messenger

    def add_handlers(self, *handlers: Handler) -> None:
        for handler in handlers:
            self._handlers.append(handler)

    def _get_telegram_id_from_update(self, update: dict) -> int | None:
        if "message" in update:
            return update["message"]["from"]["id"]
        elif "callback_query" in update:
            return update["callback_query"]["from"]["id"]
        return None

    async def dispatch(self, update: dict) -> None:
        update_id = update["update_id"]
        start_time = time.time()
        try:
            telegram_id = self._get_telegram_id_from_update(update)
            user = await self._storage.get_user(telegram_id) if telegram_id else None

            user_state = user.get("state") if user else None

            order_json_str = user["order_json"] if user and user["order_json"] else "{}"
            order_json = json.loads(order_json_str)
        except json.JSONDecodeError:
            order_json = {}

        try:
            for handler in self._handlers:
                if await handler.can_handle(
                    update,
                    user_state,
                    order_json,
                    self._storage,
                    self._messenger,
                ):
                    status = await handler.handle(
                        update,
                        user_state,
                        order_json,
                        self._storage,
                        self._messenger,
                    )
                    if status == HandlerStatus.STOP:
                        break

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                f"[DISPATCH {update_id}] ← dispatch finished - {duration_ms:.2f}ms\n"
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"[DISPATCH {update_id}] ✗ dispatch failed - {duration_ms:.2f}ms - Error: {e}\n"
            )
