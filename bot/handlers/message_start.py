import json
import logging
import time
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.storage import Storage
from bot.domain.messenger import Messenger

logger = logging.getLogger(__name__)


class MessageStart(Handler):
    async def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        return (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        )

    async def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        start_time = time.time()
        telegram_id = update["message"]["from"]["id"]

        logger.info(f"[START] → Processing /start command: {telegram_id}")

        await storage.clear_user_state_and_order(telegram_id)
        await storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

        await messenger.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text="Welcome to Pizza shop!",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        await messenger.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text="Please choose pizza type",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "Margherita", "callback_data": "pizza_margherita"},
                            {"text": "Pepperoni", "callback_data": "pizza_pepperoni"},
                        ],
                        [
                            {
                                "text": "Quattro Stagioni",
                                "callback_data": "pizza_quattro_stagioni",
                            },
                            {
                                "text": "Capricciosa",
                                "callback_data": "pizza_capricciosa",
                            },
                        ],
                        [
                            {"text": "Diavola", "callback_data": "pizza_diavola"},
                            {"text": "Prosciutto", "callback_data": "pizza_prosciutto"},
                        ],
                    ],
                }
            ),
        )

        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"[START] ← /start completed - {duration_ms:.2f}ms")

        return HandlerStatus.STOP
