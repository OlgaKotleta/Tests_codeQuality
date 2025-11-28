from bot.handlers.handler import Handler, HandlerStatus


class DatabaseHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage,
        messenger,
    ) -> bool:
        return True

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage,
        messenger,
    ) -> HandlerStatus:
        print(f"💾 Saving update to database: {update.get('update_id', 'unknown')}")
        storage.persist_update(update)
        return HandlerStatus.CONTINUE
