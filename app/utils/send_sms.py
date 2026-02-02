import httpx
from fastapi import HTTPException
from app.config import settings

SMS_API_URL = "https://api.sms.net.bd/sendsms"


def mask_phone(phone: str) -> str:
    return phone[:3] + "****" + phone[-2:]


async def send_sms(
    phone_number: str,
    message: str,
    *,
    timeout: int = 5,
    retries: int = 2
) -> bool:
    if not phone_number or len(phone_number) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number")

    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    payload = {
        "api_key": settings.SMS_API,
        "msg": message,
        "to": phone_number
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        for attempt in range(1, retries + 2):
            try:
                response = await client.post(SMS_API_URL, data=payload)

                if response.status_code == 200:
                    return True

            except httpx.RequestError as e:
                print(
                    f"SMS request failed on attempt {attempt} "
                    f"to {mask_phone(phone_number)} - Error: {str(e)}"
                )

    raise HTTPException(
        status_code=503,
        detail="Failed to send SMS. Please try again later."
    )
