import importlib
import pkgutil
import inspect

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from tzlocal import get_localzone

import tasks

# ==================================================
# SCHEDULER (ASYNCIO SAFE)
# ==================================================
scheduler = AsyncIOScheduler(timezone=get_localzone())


def is_task(func):
    return callable(func) and not func.__name__.startswith("_")


def load_tasks():
    print("Scanning task modules...")

    for _, module_name, _ in pkgutil.iter_modules(tasks.__path__):
        print(f"Importing module: tasks.{module_name}")
        module = importlib.import_module(f"tasks.{module_name}")

        for name, func in inspect.getmembers(module, is_task):
            schedule = getattr(func, "_schedule", None)
            if not schedule:
                continue

            job_id = f"{module_name}_{name}"

            try:
                # Interval or Cron
                if "seconds" in schedule or "minutes" in schedule:
                    trigger = IntervalTrigger(**schedule)
                else:
                    trigger = CronTrigger(**schedule)

                scheduler.add_job(
                    func,
                    trigger=trigger,
                    id=job_id,
                    replace_existing=True,
                )

                print(f"✔ Job added: {job_id} -> {schedule}")

            except Exception as e:
                print(f"Error scheduling {job_id}: {e}")


def start_scheduler():
    load_tasks()
    scheduler.start()
    print("APScheduler started (asyncio)")
