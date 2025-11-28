import json
from bot.domain.storage import Storage
from bot.domain.messenger import Messenger
from bot.handlers.handler import Handler, HandlerStatus


class MessageStart(Handler):
    def can_handle(
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

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]

        storage.clear_user_order_json(telegram_id)
        storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

        messenger.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="Welcome to Pizza shop!",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        messenger.send_message(
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
        return HandlerStatus.STOP
