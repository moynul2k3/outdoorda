from tortoise import Tortoise
from applications.user.models import Permission
from app.redis import redis_client

DEFAULT_ACTIONS = ["view", "add", "update", "delete"]

REDIS_DONE_KEY = "permissions:sync:done"
REDIS_LOCK_KEY = "permissions:sync:lock"

async def sync_permissions(force: bool = False):
    if not redis_client:
        raise RuntimeError("Redis not initialized")

    # Skip if already synced
    if not force and await redis_client.get(REDIS_DONE_KEY):
        print("⏭️ Permissions already synced — skipping")
        return

    # Acquire lock (30s safety)
    locked = await redis_client.set(
        REDIS_LOCK_KEY,
        "1",
        nx=True,
        ex=30
    )

    if not locked:
        print("⏳ Another worker is syncing permissions — skipping")
        return

    try:
        print("🔄 Syncing permissions...")

        apps = Tortoise.apps
        existing_models: list[str] = []
        created = 0

        for _, models in apps.items():
            for model_name, model in models.items():
                if not model.__module__.startswith("applications."):
                    continue

                model_name = model_name.lower()
                existing_models.append(model_name)

                for action in DEFAULT_ACTIONS:
                    codename = f"{action}_{model_name}"

                    _, is_created = await Permission.get_or_create(
                        codename=codename,
                        defaults={"name": f"Can {action} {model_name}"}
                    )

                    if is_created:
                        created += 1

        valid_codenames = {
            f"{action}_{m}"
            for m in existing_models
            for action in DEFAULT_ACTIONS
        }

        deleted = await Permission.exclude(
            codename__in=valid_codenames
        ).delete()

        if created == 0 and deleted == 0:
            print("✅ Permissions already up to date")
        else:
            print(f"✅ Permissions synced | created={created}, deleted={deleted}")

        # Mark as done (no expiry)
        await redis_client.set(REDIS_DONE_KEY, "1")

    finally:
        await redis_client.delete(REDIS_LOCK_KEY)
