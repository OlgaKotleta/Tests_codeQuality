import json
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.storage import Storage
from bot.domain.messenger import Messenger


class ContinueOrderHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != "ORDER_COMPLETED":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data in ["order_more", "finish_order"]

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        messenger.answerCallbackQuery(callback_query_id=update["callback_query"]["id"])

        messenger.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        if callback_data == "order_more":
            storage.clear_current_order(telegram_id)
            storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

            messenger.sendMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text="🔄 Starting new order!",
                reply_markup=json.dumps({"remove_keyboard": True}),
            )

            messenger.sendMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text="Please choose pizza type",
                reply_markup=json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "Margherita",
                                    "callback_data": "pizza_margherita",
                                },
                                {
                                    "text": "Pepperoni",
                                    "callback_data": "pizza_pepperoni",
                                },
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
                                {
                                    "text": "Prosciutto",
                                    "callback_data": "pizza_prosciutto",
                                },
                            ],
                        ],
                    }
                ),
            )
        else:
            storage.clear_current_order(telegram_id)

            history = storage.get_user_order_history(telegram_id)
            if history:
                history_text = self._format_history(history)
                messenger.sendMessage(
                    chat_id=update["callback_query"]["message"]["chat"]["id"],
                    text=f"✅ Thank you for your orders! 👋\n\nYour order history:\n{history_text}\n\nType /start anytime to order again.",
                )
            else:
                messenger.sendMessage(
                    chat_id=update["callback_query"]["message"]["chat"]["id"],
                    text="✅ Thank you for your order! See you soon! 👋\n\nType /start anytime to order again.",
                )

        return HandlerStatus.STOP

    def _format_history(self, history):
        history_text = []
        for i, order in enumerate(history[-3:], 1):
            order_data = order["order_data"]
            items = []
            if order_data.get("pizza_name"):
                items.append(
                    f"{order_data['pizza_name']} {order_data.get('pizza_size', '')}"
                )
            if order_data.get("drink") and order_data["drink"] != "No drink":
                items.append(order_data["drink"])

            if items:
                history_text.append(f"{i}. {', '.join(items)}")

        return "\n".join(history_text) if history_text else "No previous orders"
