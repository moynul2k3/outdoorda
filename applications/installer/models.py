from tortoise import fields, models



class AvailabilitySettings(models.Model):
    id = fields.UUIDField(pk=True)
    installer = fields.ForeignKeyField("models.User", related_name="installer-availability", on_delete=fields.CASCADE)
    is_available = fields.BooleanField(default=True)
    active_hourse_par_week = fields.FloatField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


    class Meta:
        table = "availability-settings"



class InstallerServiceArea(models.Model):
    id = fields.IntField(pk=True)
    installer = fields.ForeignKeyField("models.User", related_name="service_areas", on_delete=fields.CASCADE)
    area = fields.ForeignKeyField("models.ServiceArea", related_name="installers", on_delete=fields.CASCADE)

    class Meta:
        unique_together = ("installer", "area")
