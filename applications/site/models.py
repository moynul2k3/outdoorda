from tortoise import fields, models

class Terms(models.Model):
    id = fields.IntField(pk=True)
    details = fields.TextField()
    updated_at = fields.DatetimeField(auto_now=True)

class Privacy(models.Model):
    id = fields.IntField(pk=True)
    details = fields.TextField()
    updated_at = fields.DatetimeField(auto_now=True)