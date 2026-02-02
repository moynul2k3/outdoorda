from datetime import datetime, date
from typing import Optional


def format_duration(from_date: Optional[datetime]) -> Optional[str]:
    if not from_date:
        return None

    # Normalize datetime → date
    if isinstance(from_date, datetime):
        from_date = from_date.date()

    today = date.today()
    delta_days = (today - from_date).days

    if delta_days < 0:
        return "Not due yet"

    years, rem = divmod(delta_days, 365)
    months, days = divmod(rem, 30)

    parts = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")

    return ", ".join(parts) if parts else "Today"
