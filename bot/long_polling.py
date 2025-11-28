import time

from bot.dispatcher import Dispatcher
from bot.domain.messenger import Messenger


def start_long_polling(dispatcher: Dispatcher, messenger: Messenger) -> None:
    next_update_offset = 0
    while True:
        updates = messenger.getUpdates(offset=next_update_offset)
        if updates:
            for update in updates:
                next_update_offset = update["update_id"] + 1
                dispatcher.dispatch(update)
                print(".", end="", flush=True)

        time.sleep(1)
