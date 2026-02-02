import sys
import asyncio

from app.config import init_db, settings
from app.redis import init_redis
from app.utils.sync_permissions import sync_permissions
from app.dummy.registry import SEEDERS
from app.dummy.reset import reset_data


def confirm(msg: str) -> bool:
    answer = input(f"{msg} (yes/no): ").lower()
    return answer == "yes"


async def seed(apps: list[str], reset: bool):
    if settings.ENV == "production":
        print("❌ Seeding is BLOCKED in production!")
        return

    await init_db()
    init_redis()
    await sync_permissions()

    if not apps:
        print("❌ No app specified")
        print("Available:", ", ".join(SEEDERS.keys()))
        return

    if reset:
        print("⚠️ RESET ENABLED")
        await reset_data(apps)

    for app in apps:
        seeder = SEEDERS.get(app)
        if not seeder:
            print(f"❌ Unknown app: {app}")
            continue

        print(f"🌱 Seeding {app}...")
        await seeder()
        print(f"✅ {app} seeded successfully")


def main():
    args = sys.argv[1:]

    if not args or args[0] != "seed":
        print("Usage:")
        print("  python dummy.py seed user")
        print("  python dummy.py seed --all")
        print("  python dummy.py seed user --reset")
        return

    reset = "--reset" in args
    apps = [a for a in args[1:] if not a.startswith("--")]

    if "--all" in args:
        if not confirm("⚠️ This will seed ALL data. Continue?"):
            print("❌ Cancelled")
            return
        apps = list(SEEDERS.keys())

    asyncio.run(seed(apps, reset))


if __name__ == "__main__":
    main()
