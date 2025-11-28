import json
from bot.handlers.handler import Handler, HandlerStatus


class PizzaSelectionHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage,
        messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_PIZZA_NAME":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("pizza_")

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage,
        messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        pizza_name = callback_data.replace("pizza_", "").replace("_", " ").title()

        order_json["pizza_name"] = pizza_name
        storage.update_user_order_json(telegram_id, order_json)
        storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_SIZE")

        messenger.answerCallbackQuery(callback_query_id=update["callback_query"]["id"])

        messenger.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        messenger.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Please select pizza size",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "Small (25cm)", "callback_data": "size_small"},
                            {"text": "Medium (30cm)", "callback_data": "size_medium"},
                        ],
                        [
                            {"text": "Large (35cm)", "callback_data": "size_large"},
                            {"text": "Extra Large (40cm)", "callback_data": "size_xl"},
                        ],
                    ],
                }
            ),
        )
        return HandlerStatus.STOP
