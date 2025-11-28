import json

from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.storage import Storage
from bot.domain.messenger import Messenger


class Dispatcher:
    def __init__(self, storage: Storage, messenger: Messenger) -> None:
        self._handlers: list[Handler] = []
        self._storage: Storage = storage
        self._messenger: Messenger = messenger

    def unused_method(self) -> None:
        return None

    def add_handlers(self, *handlers: Handler) -> None:
        for handler in handlers:
            self._handlers.append(handler)

    def _get_telegram_id_from_update(self, update: dict) -> int | None:
        if "message" in update:
            return update["message"]["from"]["id"]
        elif "callback_query" in update:
            return update["callback_query"]["from"]["id"]
        return None

    def dispatch(self, update: dict) -> None:
        telegram_id = self._get_telegram_id_from_update(update)
        user = self._storage.get_user(telegram_id) if telegram_id else None

        user_state = user.get("state") if user else None

        order_json_str = user["order_json"] if user and user["order_json"] else "{}"
        try:
            order_json = json.loads(order_json_str)
        except json.JSONDecodeError:
            order_json = {}

        for handler in self._handlers:
            if handler.can_handle(
                update,
                user_state,
                order_json,
                self._storage,
                self._messenger,
            ):
                status = handler.handle(
                    update,
                    user_state,
                    order_json,
                    self._storage,
                    self._messenger,
                )
                if status == HandlerStatus.STOP:
                    break
