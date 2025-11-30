import logging
import time
from bot.handlers.handler import Handler, HandlerStatus
from bot.domain.storage import Storage
from bot.domain.messenger import Messenger

logger = logging.getLogger(__name__)


class DatabaseHandler(Handler):
    async def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        return True

    async def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        update_id = update.get("update_id", "unknown")
        start_time = time.time()

        logger.info(f"[DB_HANDLER] → Saving update {update_id}")

        try:
            await storage.persist_update(update)
            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                f"[DB_HANDLER] ← Saved update {update_id} - {duration_ms:.2f}ms"
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"[DB_HANDLER] ✗ Failed to save update {update_id} - {duration_ms:.2f}ms - Error: {e}"
            )

        return HandlerStatus.CONTINUE
