import sqlite3
import os
import json
from dotenv import load_dotenv

load_dotenv()


def recreate_database() -> None:
    connection = sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH"))
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
    connection.close()
    
def persist_updates(updates: list) -> None:
    if not updates:
        return
        
    connection = sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH"))
    with connection:
        data = []
        for update in updates:
            pretty_json = json.dumps(update, ensure_ascii=False, indent=2, sort_keys=True)
            data.append((pretty_json,))
        
        connection.executemany(
            "INSERT INTO telegram_updates (payload) VALUES (?)",
            data,
        )
    connection.close()

def ensure_user_exists(telegram_id: int) -> None:        
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
                    

def get_user(telegram_id: int) -> dict:
    with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
        with connection:
            cursor = connection.execute(
                "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = ?",(telegram_id,)
            )
            result = cursor.fetchone()
            if result:
                return{
                    'id':result[0],
                    'telegram_id': result[1],
                    'created_at':result[2],
                    'state':result[3],
                    'order_json':result[4]
                }
            return None

def clear_user_state_and_order(telegram_id: int)->None:
    with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
        with connection:
            connection.execute(
                "Update users SET state = NULL, order_json = NULL WHERE telegram_id = ?",
                (telegram_id,)
            )

def update_user_state(telegram_id:int, state: str)->None:
    with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
        connection.execute(
            "Update users SET state = ? WHERE telegram_id = ?",
            (state, telegram_id)
        )

def update_user_order_json(telegram_id: int, order_data: dict) -> None:
    with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
        connection.execute(
            "UPDATE users SET order_json = ? WHERE telegram_id = ?",
            (json.dumps(order_data, ensure_ascii=False), telegram_id)
        )

def save_order_to_history(telegram_id: int, order_data: dict) -> None:
    with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
        connection.execute(
            "INSERT INTO order_history (telegram_id, order_data) VALUES (?, ?)",
            (telegram_id, json.dumps(order_data, ensure_ascii=False))
        )

def get_user_order_history(telegram_id: int) -> list:
    with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
        cursor = connection.execute(
            "SELECT order_data, created_at FROM order_history WHERE telegram_id = ? ORDER BY created_at DESC",
            (telegram_id,)
        )
        results = cursor.fetchall()
        history = []
        for result in results:
            try:
                order_data = json.loads(result[0])
                history.append({
                    'order_data': order_data,
                    'created_at': result[1]
                })
            except json.JSONDecodeError:
                continue
        return history

def clear_current_order(telegram_id: int) -> None:
    with sqlite3.connect(os.getenv("SQLITE_DATABASE_PATH")) as connection:
        connection.execute(
            "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = ?",
            (telegram_id,)
        )