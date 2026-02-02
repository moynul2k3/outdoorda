from tortoise import models, fields



class Communication(models.Model):
    id = fields.IntField(pk=True)

    user = fields.ForeignKeyField("models.User", related_name="communications")
    channel = fields.CharField(max_length=50)
    template = fields.ForeignKeyField("models.MessageTemplate", related_name="communications", null=True)

    status = fields.CharField(max_length=50)
    provider_response = fields.JSONField(null=True)

    sent_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)



