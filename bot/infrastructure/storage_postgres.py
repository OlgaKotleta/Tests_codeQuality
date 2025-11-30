import json
import logging
import os
import time

import asyncpg
from dotenv import load_dotenv

from bot.domain.storage import Storage

load_dotenv()

db_logger = logging.getLogger("DB")


class StoragePostgres(Storage):
    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
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

            self._pool = await asyncpg.create_pool(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=database,
            )
        return self._pool

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def _get_connection(self):
        pool = await self._get_pool()
        return await pool.acquire()

    async def persist_updates(self, update: dict) -> None:
        sql_query = "INSERT INTO telegram_updates (payload) VALUES ($1)"
        start_time = time.time()

        db_logger.info(f"+ persist_update - {sql_query}")

        payload = json.dumps(update, ensure_ascii=False, indent=2)
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO telegram_updates (payload) VALUES ($1)", payload
                )

            duration_ms = (time.time() - start_time) * 1000
            db_logger.info(f"- persist_update - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.error(f"✗ persist_update - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def update_user_order_json(self, telegram_id: int, order_json: dict) -> None:
        sql_query = "UPDATE users SET order_json = $1 WHERE telegram_id = $2"
        start_time = time.time()

        db_logger.info(f"+ update_user_order_json - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET order_json = $1 WHERE telegram_id = $2",
                    json.dumps(order_json, ensure_ascii=False),
                    telegram_id,
                )

            duration_ms = (time.time() - start_time) * 1000
            db_logger.info(f"- update_user_order_json - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.error(
                f"✗ update_user_order_json - {duration_ms:.2f}ms - Error: {e}"
            )
            raise

    async def recreate_database(self) -> None:
        start_time = time.time()

        db_logger.info("+ recreate_database - DROP/CREATE TABLES")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute("DROP TABLE IF EXISTS telegram_updates")
                await conn.execute("DROP TABLE IF EXISTS users")
                await conn.execute("DROP TABLE IF EXISTS order_history")

                await conn.execute(
                    """
                    CREATE TABLE telegram_updates
                    (
                        id SERIAL PRIMARY KEY,
                        payload TEXT NOT NULL
                    )
                    """
                )

                await conn.execute(
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

                await conn.execute(
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

            duration_ms = (time.time() - start_time) * 1000
            db_logger.info(f"- recreate_database - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.error(f"✗ recreate_database - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def get_user(self, telegram_id: int) -> dict:
        sql_query = "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = $1"
        start_time = time.time()

        db_logger.info(f"+ get_user - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                result = await conn.fetchrow(
                    "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = $1",
                    telegram_id,
                )
                if result:
                    user_data = {
                        "id": result["id"],
                        "telegram_id": result["telegram_id"],
                        "created_at": result["created_at"],
                        "state": result["state"],
                        "order_json": result["order_json"],
                    }
                    duration_ms = (time.time() - start_time) * 1000
                    db_logger.info(f"- get_user - {duration_ms:.2f}ms")
                    return user_data

                duration_ms = (time.time() - start_time) * 1000
                db_logger.info(f"- get_user - {duration_ms:.2f}ms (no result)")
                return None
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.error(f"✗ get_user - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def clear_user_state_and_order(self, telegram_id: int) -> None:
        sql_query = (
            "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = $1"
        )
        start_time = time.time()

        db_logger.info(f"+ clear_user_state_and_order - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = $1",
                    telegram_id,
                )

            duration_ms = (time.time() - start_time) * 1000
            db_logger.info(f"- clear_user_state_and_order - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.error(
                f"✗ clear_user_state_and_order - {duration_ms:.2f}ms - Error: {e}"
            )
            raise

    async def persist_update(self, update: dict) -> None:
        await self.persist_updates([update])

    async def clear_user_order_json(self, telegram_id: int) -> None:
        sql_query = "UPDATE users SET order_json = NULL WHERE telegram_id = $1"
        start_time = time.time()

        db_logger.info(f"+ clear_user_order_json - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET order_json = NULL WHERE telegram_id = $1",
                    telegram_id,
                )

            duration_ms = (time.time() - start_time) * 1000
            db_logger.info(f"- clear_user_order_json - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.error(
                f"✗ clear_user_order_json - {duration_ms:.2f}ms - Error: {e}"
            )
            raise

    async def update_user_state(self, telegram_id: int, state: str) -> None:
        sql_query = "UPDATE users SET state = $1 WHERE telegram_id = $2"
        start_time = time.time()

        db_logger.info(f"+ update_user_state - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET state = $1 WHERE telegram_id = $2",
                    state,
                    telegram_id,
                )

            duration_ms = (time.time() - start_time) * 1000
            db_logger.info(f"- update_user_state - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.error(f"✗ update_user_state - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def ensure_user_exists(self, telegram_id: int) -> None:
        start_time = time.time()

        db_logger.info("+ ensure_user_exists - SELECT/INSERT users")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                result = await conn.fetchrow(
                    "SELECT 1 FROM users WHERE telegram_id = $1", telegram_id
                )
                if result is None:
                    await conn.execute(
                        "INSERT INTO users(telegram_id) VALUES($1)", telegram_id
                    )

            duration_ms = (time.time() - start_time) * 1000
            db_logger.info(f"- ensure_user_exists - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.error(f"✗ ensure_user_exists - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def save_order_to_history(self, telegram_id: int, order_data: dict) -> None:
        sql_query = (
            "INSERT INTO order_history (telegram_id, order_data) VALUES ($1, $2)"
        )
        start_time = time.time()

        db_logger.info(f"+ save_order_to_history - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO order_history (telegram_id, order_data) VALUES ($1, $2)",
                    telegram_id,
                    json.dumps(order_data, ensure_ascii=False),
                )

            duration_ms = (time.time() - start_time) * 1000
            db_logger.info(f"- save_order_to_history - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.error(
                f"✗ save_order_to_history - {duration_ms:.2f}ms - Error: {e}"
            )
            raise

    async def get_user_order_history(self, telegram_id: int) -> list:
        sql_query = "SELECT order_data, created_at FROM order_history WHERE telegram_id = $1 ORDER BY created_at DESC"
        start_time = time.time()

        db_logger.info(f"+ get_user_order_history - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                results = await conn.fetch(
                    "SELECT order_data, created_at FROM order_history WHERE telegram_id = $1 ORDER BY created_at DESC",
                    telegram_id,
                )

                history = []
                for result in results:
                    try:
                        order_data = json.loads(result["order_data"])
                        history.append(
                            {
                                "order_data": order_data,
                                "created_at": result["created_at"],
                            }
                        )
                    except json.JSONDecodeError:
                        continue

                duration_ms = (time.time() - start_time) * 1000
                db_logger.info(f"- get_user_order_history - {duration_ms:.2f}ms")
                return history
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.error(
                f"✗ get_user_order_history - {duration_ms:.2f}ms - Error: {e}"
            )
            raise

    async def clear_current_order(self, telegram_id: int) -> None:
        await self.clear_user_state_and_order(telegram_id)
