from bot.handlers.handler import Handler as Handler
from bot.handlers.database_handler import DatabaseHandler
from bot.handlers.ensure_users_exists import EnsureUsersExists
from bot.handlers.message_start import MessageStart
from bot.handlers.pizza_selection import PizzaSelectionHandler
from bot.handlers.pizza_size import PizzaSizeHandler
from bot.handlers.drink_selection import DrinkSelectionHandler
from bot.handlers.order_confirmation import OrderConfirmationHandler
from bot.handlers.continue_order import ContinueOrderHandler


def get_handlers():
    return [
        DatabaseHandler(),
        EnsureUsersExists(),
        MessageStart(),
        PizzaSelectionHandler(),
        PizzaSizeHandler(),
        DrinkSelectionHandler(),
        OrderConfirmationHandler(),
        ContinueOrderHandler(),
    ]
