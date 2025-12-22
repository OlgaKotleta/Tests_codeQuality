import asyncio
import json
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Update, PhotoSize
from aiogram.utils.serialization import deserialize_telegram_object_to_python
import dotenv

dotenv.load_dotenv()

dispatcher = Dispatcher()

@dispatcher.message(F.text)
async def echo_text_handler(message: Message):
    await message.answer(f"You say: {message.text}")

@dispatcher.message(F.photo)
async def echo_photo_handler(message: Message, bot: Bot):
    photo: PhotoSize = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo.file_id,
    )

@dispatcher.update.outer_middleware()
async def logger_middleware(handler: callable, event: Update, data: dict):
    payload = deserialize_telegram_object_to_python(event)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return await handler(event, data)

async def main() -> None:
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())