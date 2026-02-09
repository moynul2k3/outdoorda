import uuid
from tortoise import models, fields


class PushNotification(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="notifications")
    title = fields.CharField(max_length=255, null=True)
    body = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    is_read = fields.BooleanField(default=False)

    class Meta:
        table = "notifications"

class NotificationSetting(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    user = fields.ForeignKeyField("models.User", related_name="notification_settings")
    push_notification = fields.BooleanField(default=True)
    email_notification = fields.BooleanField(default=True)

    class Meta:
        table = "notification_settings"