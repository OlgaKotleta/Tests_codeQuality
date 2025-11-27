from bot.dispatcher import Dispatcher
from bot import database_client
from bot import telegram_client
import time

def start_long_polling(dispatcher: Dispatcher) -> None:
    next_update_offset = 0
    while True:
        updates = telegram_client.getUpdates(offset=next_update_offset)
        
        if updates:
            for update in updates:
                next_update_offset = update["update_id"] + 1
                dispatcher.dispatch(update) 
                print(".", end="", flush=True)
                        
        time.sleep(1)