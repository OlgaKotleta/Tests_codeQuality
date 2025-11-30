import pytest
from bot.dispatcher import Dispatcher
from bot.handlers.pizza_size import PizzaSizeHandler
from tests.mocks import Mock


@pytest.mark.asyncio
async def test_pizza_size_handler():
    test_update = {
        "update_id": 12345679,
        "callback_query": {
            "id": "callback124",
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "message": {
                "message_id": 101,
                "chat": {
                    "id": 12345,
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private",
                },
                "date": 1640995300,
            },
            "data": "size_medium",
        },
    }

    update_order_json_called = False
    update_user_state_called = False

    async def update_user_order_json(telegram_id: int, order_json: dict) -> None:
        assert telegram_id == 12345
        assert order_json["pizza_size"] == "Medium (30cm)"
        nonlocal update_order_json_called
        update_order_json_called = True

    async def update_user_state(telegram_id: int, state: str) -> None:
        assert telegram_id == 12345
        assert state == "WAIT_FOR_DRINKS"
        nonlocal update_user_state_called
        update_user_state_called = True

    async def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return {
            "state": "WAIT_FOR_PIZZA_SIZE",
            "order_json": '{"pizza_name": "Margherita"}',
        }

    answer_callback_called = False
    delete_message_called = False
    send_message_called = False

    async def answerCallbackQuery(callback_query_id: str, **kwargs) -> dict:
        assert callback_query_id == "callback124"
        nonlocal answer_callback_called
        answer_callback_called = True
        return {"ok": True}

    async def deleteMessage(chat_id: int, message_id: int) -> dict:
        assert chat_id == 12345
        assert message_id == 101
        nonlocal delete_message_called
        delete_message_called = True
        return {"ok": True}

    async def sendMessage(chat_id: int, text: str, **kwargs) -> dict:
        assert chat_id == 12345
        assert "Now choose a drink" in text
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
    pizza_size_handler = PizzaSizeHandler()
    dispatcher.add_handlers(pizza_size_handler)

    await dispatcher.dispatch(test_update)

    assert update_order_json_called
    assert update_user_state_called
    assert answer_callback_called
    assert delete_message_called
    assert send_message_called
