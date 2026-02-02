from fastapi import APIRouter
from twilio.rest import Client
from app.config import settings



router = APIRouter()





account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN




@router.get("/message")
def whatsapp_message(phone: str, message: str):
    client = Client(account_sid, auth_token)
    # Don't overwrite phone argument
    message = client.messages.create(
        from_="whatsapp:+14155238886", 
        body=message,
        to=f"whatsapp:+88{phone}"
    )
    print(message)
    return "success"
