from pydantic import EmailStr
from app.utils.send_email import send_email

async def email_notify(subject: str, from_email: EmailStr, to: EmailStr, message: str):
    await send_email(
        subject=subject,
        from_email=from_email,
        to=to,
        message=message,
        html_message=message,
    )