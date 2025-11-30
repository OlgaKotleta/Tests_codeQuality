from bot.infrastructure.storage_postgres import StoragePostgres

StoragePostgres().recreate_database()
print("Database postgres ready\n")
