import sqlite3
import os
import json

from bot.domain.storage import Storage

from dotenv import load_dotenv

load_dotenv()


class StorageSqlite(Storage):
    def recreate_database() -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                connection.execute("DROP TABLE IF EXISTS telegram_updates")
                connection.execute("DROP TABLE IF EXISTS users")
                connection.execute("DROP TABLE IF EXISTS order_history")

                connection.execute(
                    """
                    CREATE TABLE telegram_updates
                    (
                        id INTEGER PRIMARY KEY,
                        payload TEXT NOT NULL
                    )
                    """
                )

                connection.execute(
                    """
                    CREATE TABLE users
                    (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        state TEXT DEFAULT NULL,
                        order_json TEXT DEFAULT NULL
                    )
                    """
                )

                connection.execute(
                    """
                    CREATE TABLE order_history
                    (
                        id INTEGER PRIMARY KEY,
                        telegram_id INTEGER NOT NULL,
                        order_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

    def persist_updates(self, update: dict) -> None:
        payload = json.dumps(update, ensure_ascii=False, indent=2)
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                connection.execute(
                    "INSERT INTO telegram_updates (payload) VALUES (?)", (payload,)
                )

    def ensure_user_exists(self, telegram_id: int) -> None:
        """Ensure a user with the given telegram_id exists in the users table."""
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            cursor = connection.execute(
                "SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,)
            )
            if cursor.fetchone() is None:
                print(f"👤 Creating new user: {telegram_id}")
                connection.execute(
                    "INSERT INTO users(telegram_id) VALUES(?)", (telegram_id,)
                )
            else:
                print(f"👤 User already exists: {telegram_id}")

    def get_user(self, telegram_id: int) -> dict:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                cursor = connection.execute(
                    "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = ?",
                    (telegram_id,),
                )
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "telegram_id": result[1],
                        "created_at": result[2],
                        "state": result[3],
                        "order_json": result[4],
                    }
                return None

    def clear_user_state_and_order(self, telegram_id: int) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                connection.execute(
                    "Update users SET state = NULL, order_json = NULL WHERE telegram_id = ?",
                    (telegram_id,),
                )

    def update_user_order_json(self, telegram_id: int, order_json: dict) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            with connection:
                connection.execute(
                    "UPDATE users SET order_json = ? WHERE telegram_id = ?",
                    (json.dumps(order_json, ensure_ascii=False), telegram_id),
                )

    def save_order_to_history(self, telegram_id: int, order_data: dict) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            connection.execute(
                "INSERT INTO order_history (telegram_id, order_data) VALUES (?, ?)",
                (telegram_id, json.dumps(order_data, ensure_ascii=False)),
            )

    def get_user_order_history(self, telegram_id: int) -> list:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            cursor = connection.execute(
                "SELECT order_data, created_at FROM order_history WHERE telegram_id = ? ORDER BY created_at DESC",
                (telegram_id,),
            )
            results = cursor.fetchall()
            history = []
            for result in results:
                try:
                    order_data = json.loads(result[0])
                    history.append({"order_data": order_data, "created_at": result[1]})
                except json.JSONDecodeError:
                    continue
            return history

    def clear_current_order(self, telegram_id: int) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            connection.execute(
                "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = ?",
                (telegram_id,),
            )

    def persist_update(self, update: dict) -> None:
        self.persist_updates([update])

    def clear_user_order_json(self, telegram_id: int) -> None:
        with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
            connection.execute(
                "UPDATE users SET order_json = NULL WHERE telegram_id = ?",
                (telegram_id,),
            )
