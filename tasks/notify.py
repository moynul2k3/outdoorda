from app.utils.task_decorators import every
from app.utils.send_email import send_email

@every(seconds=30)
def check_every_schedule():
    print("wake up Call")



@every(hour=8, minute=0)
async def check_email_schedule():
    await send_email(
        subject="Good Morning Message",
        to=["softvence.moynul@gmail.com"],
        html_message="<h3>Hello Moynul! </h3><p>Good Morning. How are you.</p>",
        from_name="My App",
        from_email='moynul.officials@gmail.com'
    )
    print("send Good Morning email everyday at 8:00 AM")
    
    