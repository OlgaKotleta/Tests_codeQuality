import json
import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler, HandlerStatus

class DrinkSelectionHandler(Handler):
    def can_handle(self, update, state, order_json) -> bool:
        if "callback_query" not in update:
            return False
    
        if state != "WAIT_FOR_DRINKS":
            return False
        
        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("drink_")
    
    def handle(self, update, state, order_json) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        drink_mapping = {
            "drink_coke": "Coca-Cola",
            "drink_pepsi": "Pepsi",
            "drink_fanta": "Fanta",
            "drink_sprite": "Sprite",
            "drink_water": "Water",
            "drink_none": "No drink",
        }

        drink = drink_mapping.get(callback_data)
        order_json["drink"] = drink
        
        bot.database_client.update_user_order_json(telegram_id, order_json)
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_CONFIRMATION")

        bot.telegram_client.answerCallbackQuery(
            callback_query_id=update["callback_query"]["id"]
        )

        bot.telegram_client.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"]
        )
        order_summary = self._format_order_summary(order_json)
        
        bot.telegram_client.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text=f"📋 Your order:\n{order_summary}\n\nPlease confirm your order:",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "✅ Confirm Order", "callback_data": "confirm_yes"},
                            {"text": "❌ Cancel", "callback_data": "confirm_no"},
                        ]
                    ],
                }
            ),
        )
        return HandlerStatus.STOP
    
    def _format_order_summary(self, order_json: dict) -> str:
        summary = []
        if order_json.get("pizza_name"):
            summary.append(f"🍕 Pizza: {order_json['pizza_name']}")
        if order_json.get("pizza_size"):
            summary.append(f"📏 Size: {order_json['pizza_size']}")
        if order_json.get("drink"):
            summary.append(f"🥤 Drink: {order_json['drink']}")
        return "\n".join(summary)