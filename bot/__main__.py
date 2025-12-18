import asyncio
import json
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    CallbackQuery,
    Message,
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.serialization import deserialize_telegram_object_to_python

import dotenv


dotenv.load_dotenv()


dispatcher = Dispatcher()


class Order(StatesGroup):
    wait_for_pizza_name = State()
    wait_for_pizza_size = State()
    wait_for_drinks = State()
    wait_for_order_approve = State()
    wait_for_payment = State()
    order_finished = State()


@dispatcher.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    PIZZA_NAMES = ["margherita", "pepperoni", "capricciosa", "diavola", "prosciutto"]
    await message.answer(
        "Select pizza",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{pizza_name.capitalize()}",
                        callback_data=f"pizza_{pizza_name}",
                    ),
                ]
                for pizza_name in PIZZA_NAMES
            ]
        ),
    )
    await state.set_state(Order.wait_for_pizza_name)


@dispatcher.callback_query(Order.wait_for_pizza_name)
async def pizza_name_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    PIZZA_SIZES = ["small", "medium", "large", "xl"]
    await asyncio.gather(
        bot.answer_callback_query(callback.id),
        bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
        ),
        bot.send_message(
            chat_id=callback.message.chat.id,
            text="Please select pizza size",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=f"{pizza_size.capitalize()}",
                            callback_data=f"size_{pizza_size}",
                        ),
                    ]
                    for pizza_size in PIZZA_SIZES
                ]
            ),
        ),
        state.set_state(Order.wait_for_drinks),
    )



@dispatcher.update.outer_middleware()
async def database_injector_middleware(handler: callable, event: Update, data: dict):
    payload = deserialize_telegram_object_to_python(event)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return await handler(event, data)


async def main() -> None:
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())