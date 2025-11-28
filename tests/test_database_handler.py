from bot.dispatcher import Dispatcher
from bot.handlers.database_handler import DatabaseHandler

from tests.mocks import Mock


def test_database_handler_execution():
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
            "text": "Hello, this is a test message",
        },
    }

    persist_updates_called = False

    def persist_updates(updates: list) -> None:
        nonlocal persist_updates_called
        persist_updates_called = True
        assert updates == [test_update]

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return None

    mock_storage = Mock(
        {
            "persist_updates": persist_updates,
            "get_user": get_user,
        }
    )
    mock_messenger = Mock({})

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    update_logger = DatabaseHandler()
    dispatcher.add_handler(update_logger)
    dispatcher.dispatch(test_update)

    assert persist_updates_called
