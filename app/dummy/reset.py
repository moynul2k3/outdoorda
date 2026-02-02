from tortoise import Tortoise

RESET_TABLES = {
    "user": ["user"],
}


async def reset_data(apps: list[str]):
    conn = Tortoise.get_connection("default")

    for app in apps:
        tables = RESET_TABLES.get(app, [])
        for table in tables:
            print(f"🧹 Truncating table: {table}")
            await conn.execute_script(f"DELETE FROM {table};")
