import pytest
from bot.dispatcher import Dispatcher
from bot.handlers.pizza_selection import PizzaSelectionHandler
from tests.mocks import Mock


@pytest.mark.asyncio
async def test_pizza_selection_handler():
    test_update = {
        "update_id": 12345678,
        "callback_query": {
            "id": "callback123",
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "message": {
                "message_id": 100,
                "chat": {
                    "id": 12345,
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private",
                },
                "date": 1640995200,
            },
            "data": "pizza_margherita",
        },
    }

    update_order_json_called = False
    update_user_state_called = False

    async def update_user_order_json(telegram_id: int, order_json: dict) -> None:
        assert telegram_id == 12345
        assert order_json["pizza_name"] == "Margherita"
        nonlocal update_order_json_called
        update_order_json_called = True

    async def update_user_state(telegram_id: int, state: str) -> None:
        assert telegram_id == 12345
        assert state == "WAIT_FOR_PIZZA_SIZE"
        nonlocal update_user_state_called
        update_user_state_called = True

    async def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return {"state": "WAIT_FOR_PIZZA_NAME", "order_json": "{}"}

    answer_callback_called = False
    delete_message_called = False
    send_message_called = False

    async def answerCallbackQuery(callback_query_id: str, **kwargs) -> dict:
        assert callback_query_id == "callback123"
        nonlocal answer_callback_called
        answer_callback_called = True
        return {"ok": True}

    async def deleteMessage(chat_id: int, message_id: int) -> dict:
        assert chat_id == 12345
        assert message_id == 100
        nonlocal delete_message_called
        delete_message_called = True
        return {"ok": True}

    async def sendMessage(chat_id: int, text: str, **kwargs) -> dict:
        assert chat_id == 12345
        assert text == "Please select pizza size"
        nonlocal send_message_called
        send_message_called = True
        return {"ok": True}

    mock_storage = Mock(
        {
            "update_user_order_json": update_user_order_json,
            "update_user_state": update_user_state,
            "get_user": get_user,
        }
    )

    mock_messenger = Mock(
        {
            "answerCallbackQuery": answerCallbackQuery,
            "deleteMessage": deleteMessage,
            "sendMessage": sendMessage,
        }
    )

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    pizza_handler = PizzaSelectionHandler()
    dispatcher.add_handlers(pizza_handler)

    await dispatcher.dispatch(test_update)

    assert update_order_json_called
    assert update_user_state_called
    assert answer_callback_called
    assert delete_message_called
    assert send_message_called
