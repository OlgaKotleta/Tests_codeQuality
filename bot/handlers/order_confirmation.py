import json
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.storage import Storage
from bot.domain.messenger import Messenger


class OrderConfirmationHandler(Handler):
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

        if state != "WAIT_FOR_CONFIRMATION":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("confirm_")

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

        if callback_data == "confirm_yes":
            storage.save_order_to_history(telegram_id, order_json)

            order_summary = self._format_order_summary(order_json)

            messenger.sendMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text=f"✅ Order confirmed!\n\n{order_summary}\n\nThank you for your order! 🎉",
            )

            storage.update_user_state(telegram_id, "ORDER_COMPLETED")

            messenger.sendMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text="What would you like to do next?",
                reply_markup=json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "🔄 Order More",
                                    "callback_data": "order_more",
                                },
                                {"text": "✅ Finish", "callback_data": "finish_order"},
                            ]
                        ],
                    }
                ),
            )
        else:
            messenger.sendMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text="❌ Order cancelled.\nType /start to begin again.",
            )
            storage.clear_current_order(telegram_id)

        return HandlerStatus.STOP

    def _format_order_summary(self, order_json):
        summary = []
        if order_json.get("pizza_name"):
            summary.append(f"🍕 Pizza: {order_json['pizza_name']}")
        if order_json.get("pizza_size"):
            summary.append(f"📏 Size: {order_json['pizza_size']}")
        if order_json.get("drink"):
            summary.append(f"🥤 Drink: {order_json['drink']}")
        return "\n".join(summary)
