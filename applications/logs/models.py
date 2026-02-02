from tortoise import models, fields

class AuditLog(models.Model):
    id = fields.IntField(pk=True)

    user = fields.ForeignKeyField("models.User", null=True)
    action = fields.CharField(max_length=255)
    entity = fields.CharField(max_length=255)
    entity_id = fields.IntField()

    ip_address = fields.CharField(max_length=50)

    created_at = fields.DatetimeField(auto_now_add=True)


class SyncLog(models.Model):
    id = fields.IntField(pk=True)

    source = fields.CharField(max_length=50)
    status = fields.CharField(max_length=50)

    total_records = fields.IntField()
    error_message = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
