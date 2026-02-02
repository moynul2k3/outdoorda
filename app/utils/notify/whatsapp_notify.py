from app.utils.send_email import send_email

async def email_notify(subject: str, message: str):
    await send_email(
        subject=subject,
        message=message,
        html_message=message,
    )