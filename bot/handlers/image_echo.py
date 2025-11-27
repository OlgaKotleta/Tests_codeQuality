from bot.handlers.handler import Handler
import bot.telegram_client

class ImageEcho(Handler):
    def can_handle(self, update: dict) -> bool:
        return "message" in update and "photo" in update["message"]
    
    def handle(self, update: dict) -> bool:
        photo = update["message"]["photo"][-1]
        
        bot.telegram_client.sendPhoto(
            chat_id=update["message"]["chat"]["id"],
            photo=photo["file_id"]
        )
        
        return False