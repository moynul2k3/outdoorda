from tortoise import fields, models
import uuid


class Pet(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    owner = fields.ForeignKeyField("models.User", related_name="pets")
    name = fields.CharField(max_length=100)
    type = fields.CharField(max_length=100)
    breed = fields.CharField(max_length=100, null=True)
    size = fields.CharField(max_length=100, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "pets"