import logging
import time
from bot.domain.storage import Storage
from bot.domain.messenger import Messenger
from bot.handlers.handler import Handler, HandlerStatus

logger = logging.getLogger(__name__)


class EnsureUsersExists(Handler):
    async def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        return "message" in update and "from" in update["message"]

    async def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        start_time = time.time()
        telegram_id = update["message"]["from"]["id"]

        logger.info(f"[USER] → Ensuring user exists: {telegram_id}")

        await storage.ensure_user_exists(telegram_id)

        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"[USER] ← User ensured - {duration_ms:.2f}ms")

        return HandlerStatus.CONTINUE
