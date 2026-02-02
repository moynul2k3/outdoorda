from tortoise import fields
from tortoise.models import Model
STATUS = (
    ('daily', "Daily"),
    ('weekly', "Weekly"),
    ('monthly', "Monthly"),
)

class UserSettings(Model):
    user  = fields.ForeignKeyField('models.User', on_delete=fields.CASCADE)

    # reminder
    email_notifications = fields.BooleanField(default=True)
    whatsapp_notifications = fields.BooleanField(default=True)
    call_reminder_notifications = fields.BooleanField(default=True)

    reminder_frequency = fields.CharField(max_length=100, default='daily', choices=STATUS)

    # alert
    daily_summery_alert = fields.BooleanField(default=True)
    performance_alert = fields.BooleanField(default=True)

    # Schedule
    work_hour_start = fields.TextField(null=True)
    work_hour_end = fields.TextField(null=True)

    class Meta:
        table = "user_settings"



class WorkHoursSettings(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', on_delete=fields.CASCADE)  
    start_time = fields.TimeField()
    end_time = fields.TimeField()
    timezone = fields.CharField(max_length=100)

    class Meta:
        table = "work_hours_settings"

    

