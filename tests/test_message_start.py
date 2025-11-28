from bot.dispatcher import Dispatcher
from bot.handlers.message_start import MessageStart

from tests.mocks import Mock


def test_message_start_handler():
    test_update = {
        "update_id": 12345678,
        "message": {
            "message_id": 1,
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "chat": {
                "id": 12345,
                "first_name": "Test",
                "username": "testuser",
                "type": "private",
            },
            "date": 1640995200,
            "text": "/start",
        },
    }

    clear_user_data_called = False
    update_user_state_called = False

    def clear_user_order_json(telegram_id: int) -> None:
        assert telegram_id == 12345

        nonlocal clear_user_data_called
        clear_user_data_called = True

    def update_user_state(telegram_id: int, state: str) -> None:
        assert telegram_id == 12345
        assert state == "WAIT_FOR_PIZZA_NAME"

        nonlocal update_user_state_called
        update_user_state_called = True

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return {"state": None, "order_json": "{}"}

    send_message_calls = []

    def send_message(chat_id: int, text: str, **kwargs) -> dict:
        assert chat_id == 12345
        send_message_calls.append({"text": text, "kwargs": kwargs})
        return {"ok": True}

    mock_storage = Mock(
        {
            "clear_user_order_json": clear_user_order_json,
            "update_user_state": update_user_state,
            "get_user": get_user,
        }
    )
    mock_messenger = Mock({"send_message": send_message})

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handler(MessageStart())

    dispatcher.dispatch(test_update)

    assert clear_user_data_called
    assert update_user_state_called

    assert len(send_message_calls) == 2
    assert send_message_calls[0]["text"] == "Welcome to Pizza shop!"
    assert send_message_calls[1]["text"] == "Please choose pizza type"
