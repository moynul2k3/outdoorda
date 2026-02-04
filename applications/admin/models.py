from tortoise import models, fields
import uuid





class ContactInfo(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    admin = fields.ForeignKeyField("models.User", related_name="contact_infos")
    phone_number = fields.CharField(max_length=20)
    email = fields.CharField(max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "contact_infos"



class FAQ(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    question = fields.TextField()
    answer = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "faqs"



class CustomerInfo(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    post_request = fields.ForeignKeyField("models.PostRequest", related_name="customer_info")
    cust_name = fields.CharField(max_length=100, null=True)
    cust_email = fields.CharField(max_length=100, null=True)
    cust_phone = fields.CharField(max_length=20, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


    class Meta:
        table = "customer_info"


