from tortoise import fields, models
from tortoise.validators import MinValueValidator, MaxValueValidator




class InstallerReview(models.Model):
    id = fields.IntField(pk=True)
    installer = fields.ForeignKeyField("models.User", related_name="installer", on_delete=fields.CASCADE)
    user = fields.ForeignKeyField('models.User', on_delete=fields.CASCADE, related_name='installer_reviews') 
    rating = fields.IntField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True)
    review = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
