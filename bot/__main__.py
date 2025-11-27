from bot.dispatcher import Dispatcher
from bot.handlers import get_handlers
from bot.long_polling import start_long_polling

if __name__ == "__main__":
    try:
        dispatcher = Dispatcher()
        handlers = get_handlers()
        dispatcher.add_handler(*handlers)
        start_long_polling(dispatcher)    
    except KeyboardInterrupt:
        print("\nBot stopped")