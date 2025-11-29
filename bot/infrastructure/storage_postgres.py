import json
import os

import pg8000
from dotenv import load_dotenv

from bot.domain.storage import Storage

load_dotenv()


class StoragePostgres(Storage):
    def _get_connection(self):
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DATABASE")

        if host is None:
            raise ValueError("POSTGRES_HOST environment is not set")

        if port is None:
            raise ValueError("POSTGRES_PORT environment is not set")

        if user is None:
            raise ValueError("POSTGRES_USER environment is not set")

        if password is None:
            raise ValueError("POSTGRES_PASSWORD environment is not set")

        if database is None:
            raise ValueError("POSTGRES_DATABASE environment is not set")

        return pg8000.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
        )

    def persist_updates(self, update: dict) -> None:
        payload = json.dumps(update, ensure_ascii=False, indent=2)
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO telegram_updates (payload) VALUES (%s)", (payload,)
                )
            conn.commit()

    def update_user_order_json(self, telegram_id: int, order_json: dict) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET order_json = %s WHERE telegram_id = %s",
                    (json.dumps(order_json, ensure_ascii=False), telegram_id),
                )
            conn.commit()

    def recreate_database(self) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS telegram_updates")
                cursor.execute("DROP TABLE IF EXISTS users")
                cursor.execute("DROP TABLE IF EXISTS order_history")

                cursor.execute(
                    """
                    CREATE TABLE telegram_updates
                    (
                        id SERIAL PRIMARY KEY,
                        payload TEXT NOT NULL
                    )
                    """
                )

                cursor.execute(
                    """
                    CREATE TABLE users
                    (
                        id SERIAL PRIMARY KEY,
                        telegram_id BIGINT NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        state TEXT DEFAULT NULL,
                        order_json TEXT DEFAULT NULL
                    )
                    """
                )

                cursor.execute(
                    """
                    CREATE TABLE order_history
                    (
                        id SERIAL PRIMARY KEY,
                        telegram_id INTEGER NOT NULL,
                        order_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            conn.commit()

    def get_user(self, telegram_id: int) -> dict:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = %s",
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
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = %s",
                    (telegram_id,),
                )
            conn.commit()

    def persist_update(self, update: dict) -> None:
        self.persist_updates([update])

    def clear_user_order_json(self, telegram_id: int) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET order_json = NULL WHERE telegram_id = %s",
                    (telegram_id,),
                )
            conn.commit()

    def update_user_state(self, telegram_id: int, state: str) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET state = %s WHERE telegram_id = %s",
                    (state, telegram_id),
                )
            conn.commit()

    def ensure_user_exists(self, telegram_id: int) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM users WHERE telegram_id = %s", (telegram_id,)
                )
                if cursor.fetchone() is None:
                    print(f"👤 Creating new user: {telegram_id}")
                    cursor.execute(
                        "INSERT INTO users(telegram_id) VALUES(%s)", (telegram_id,)
                    )
                else:
                    print(f"👤 User already exists: {telegram_id}")
            conn.commit()

    def save_order_to_history(self, telegram_id: int, order_data: dict) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO order_history (telegram_id, order_data) VALUES (%s, %s)",
                    (telegram_id, json.dumps(order_data, ensure_ascii=False)),
                )
            conn.commit()

    def get_user_order_history(self, telegram_id: int) -> list:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT order_data, created_at FROM order_history WHERE telegram_id = %s ORDER BY created_at DESC",
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
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = %s",
                    (telegram_id,),
                )
