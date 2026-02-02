from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Union

from app.utils.send_email import send_email
router = APIRouter(prefix="/communications", tags=["Communications"])



class EmailPayload(BaseModel):
    subject: str
    to: Union[EmailStr, List[EmailStr]]
    message: Optional[str] = None
    html_message: Optional[str] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    reply_to: Optional[List[EmailStr]] = None



@router.post("/send-email")
async def send_dynamic_email(payload: EmailPayload):
    try:
        result = await send_email(
            subject=payload.subject,
            to=payload.to,
            message=payload.message,
            html_message=payload.html_message,
            from_email=payload.from_email,
            from_name=payload.from_name,
            cc=payload.cc,
            bcc=payload.bcc,
            reply_to=payload.reply_to,
        )
        if result:
            return {"message": "Email sent successfully", "recipients": payload.to}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
