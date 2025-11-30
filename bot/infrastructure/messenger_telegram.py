import logging
import os
import time

import aiohttp
from dotenv import load_dotenv

from bot.domain.messenger import Messenger

load_dotenv()

http_logger = logging.getLogger("HTTP")


class MessengerTelegram(Messenger):
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    def _get_telegram_base_uri(self) -> str:
        return f"https://api.telegram.org/bot{os.getenv('TOKEN')}"

    def _get_telegram_file_uri(self) -> str:
        return f"https://api.telegram.org/file/bot{os.getenv('TOKEN')}"

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _make_request(self, method: str, **kwargs) -> dict:
        url = f"{self._get_telegram_base_uri()}/{method}"
        start_time = time.time()

        http_logger.info(f"+ POST {method}")

        try:
            session = await self._get_session()
            async with session.post(
                url,
                json=kwargs,
                headers={"Content-Type": "application/json"},
            ) as response:
                response_json = await response.json()
                assert response_json["ok"]

                duration_ms = (time.time() - start_time) * 1000
                http_logger.info(f"- POST {method} - {duration_ms:.2f}ms")

                return response_json["result"]
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            http_logger.error(f"✗ POST {method} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def close(self) -> None:
        """Закрыть HTTP сессию."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def sendMessage(self, chat_id: int, text: str, **kwargs) -> dict:
        return await self._make_request(
            "sendMessage", chat_id=chat_id, text=text, **kwargs
        )

    async def getUpdates(self, **kwargs) -> dict:
        return await self._make_request("getUpdates", **kwargs)

    async def answerCallbackQuery(self, callback_query_id: str, **kwargs) -> dict:
        return await self._make_request(
            "answerCallbackQuery",
            callback_query_id=callback_query_id,
            **kwargs,
        )

    async def deleteMessage(self, chat_id: int, message_id: int) -> dict:
        return await self._make_request(
            "deleteMessage",
            chat_id=chat_id,
            message_id=message_id,
        )
