import json
import bot.telegram_client
import bot.database_client
from bot.handlers.handler import Handler, HandlerStatus

class PizzaSizeHandler(Handler):
    def can_handle(self, update, state, order_json) -> bool:
        if "callback_query" not in update:
            return False
    
        if state != "WAIT_FOR_PIZZA_SIZE":
            return False
        
        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("size_")
    
    def handle(self, update, state, order_json) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        size_mapping = {
            "size_small": "Small (25cm)",
            "size_medium": "Medium (30cm)",
            "size_large": "Large (35cm)",
            "size_xl": "XL (40cm)",
        }

        pizza_size = size_mapping.get(callback_data)
        order_json["pizza_size"] = pizza_size
        
        bot.database_client.update_user_order_json(telegram_id, order_json)
        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_DRINKS")

        bot.telegram_client.answerCallbackQuery(
            callback_query_id=update["callback_query"]["id"]
        )

        bot.telegram_client.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"]
        )

        bot.telegram_client.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text=f"Great! {order_json.get('pizza_name')} - {pizza_size}\n\nNow choose a drink:",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "🥤 Coca-Cola", "callback_data": "drink_coke"},
                            {"text": "🥤 Pepsi", "callback_data": "drink_pepsi"},
                        ],
                        [
                            {"text": "🥤 Fanta", "callback_data": "drink_fanta"},
                            {"text": "🥤 Sprite", "callback_data": "drink_sprite"},
                        ],
                        [
                            {"text": "💧 Water", "callback_data": "drink_water"},
                            {"text": "🚫 No drink", "callback_data": "drink_none"},
                        ],
                    ],
                }
            ),
        )
        
        return HandlerStatus.STOP