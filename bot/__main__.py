import asyncio
import logging

import bot.long_polling
from bot.dispatcher import Dispatcher
from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers import get_handlers
from bot.infrastructure.messenger_telegram import MessengerTelegram
from bot.infrastructure.storage_postgres import StoragePostgres

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def main() -> None:
    storage: Storage = StoragePostgres()
    messenger: Messenger = MessengerTelegram()

    try:
        dispatcher = Dispatcher(storage, messenger)
        dispatcher.add_handlers(*get_handlers())
        await bot.long_polling.start_long_polling(dispatcher, messenger)
    except KeyboardInterrupt:
        print("\nBye!")
    finally:
        if hasattr(messenger, "close"):
            await messenger.close()
        if hasattr(storage, "close"):
            await storage.close()


if __name__ == "__main__":
    asyncio.run(main())
