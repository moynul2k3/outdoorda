from fastapi import APIRouter, HTTPException, Depends, Form
from applications.user.models import User
from applications.site.settings import UserSettings, WorkHoursSettings
from app.auth import login_required
from datetime import time
from pydantic import BaseModel, field_validator
from app.token import get_current_user

router = APIRouter(prefix="/user-settings", tags=["User Settings"])

STATUS_CHOICES = ("daily", "weekly", "monthly")


# schemas.py (Pydantic)


class WorkHoursUpdate(BaseModel):
    start_time: time
    end_time: time
    timezone: str  

    @field_validator("timezone")
    def validate_tz(cls, v: str) -> str:
        # keep it simple here: just ensure non-empty
        if not v.strip():
            raise ValueError("Timezone is required")
        return v



# -----------------------------
# Get user settings for logged-in user
# -----------------------------
@router.get("/", response_model=dict)
async def get_user_settings(user: User = Depends(login_required)):
    settings = await UserSettings.get_or_none(user=user)
    if not settings:
        settings = await UserSettings.create(user=user)

    return {
        "user_id": str(settings.user_id),
        "email_notifications": settings.email_notifications,
        "whatsapp_notifications": settings.whatsapp_notifications,
        "call_reminder_notifications": settings.call_reminder_notifications,
        "reminder_frequency ": settings.reminder_frequency,


        "daily_summery_alert": settings.daily_summery_alert,
        "performance_alert": settings.performance_alert,

        "work_hour_start": settings.work_hour_start,
        "work_hour_end": settings.work_hour_end,
    }


# -----------------------------
# Create or update user settings using Form
# -----------------------------
@router.patch("/", response_model=dict)
async def create_or_update_user_settings(
    email_notifications: bool = Form(True),
    whatsapp_notifications: bool = Form(True),
    call_reminder_notifications: bool = Form(True),
    reminder_frequency: str = Form("daily"),

    daily_summery_alert: bool = Form(True),
    performance_alert: bool = Form(True),

    work_hour_start: str | None = Form("09:00"),
    work_hour_end: str | None = Form("17:00"),
    user: User = Depends(login_required)
):
    # Validate status
    if reminder_frequency not in STATUS_CHOICES:
        raise HTTPException(status_code=400, detail="Invalid status choice")

    data = {
        "email_notifications": email_notifications,
        "whatsapp_notifications": whatsapp_notifications,
        "call_reminder_notifications": call_reminder_notifications,
        "daily_summery_alert": daily_summery_alert,
        "performance_alert": performance_alert,
        "reminder_frequency": reminder_frequency,
        "work_hour_start": work_hour_start,
        "work_hour_end": work_hour_end,
    }

    settings = await UserSettings.get_or_none(user=user)

    if settings:
        await settings.update_from_dict(data)
        await settings.save()
        await settings.fetch_related('user')
    else:
        settings = await UserSettings.create(user=user, **data)
        await settings.fetch_related('user')

    return {
        "user_id": str(settings.user.id),
        "email_notifications": settings.email_notifications,
        "whatsapp_notifications": settings.whatsapp_notifications,
        "call_reminder_notifications": settings.call_reminder_notifications,
        "reminder_frequency": settings.reminder_frequency,

        "daily_summery_alert": settings.daily_summery_alert,
        "performance_alert": settings.performance_alert,

        "work_hour_start": settings.work_hour_start,
        "work_hour_end": settings.work_hour_end,
    }


