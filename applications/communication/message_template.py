from tortoise import fields, models
from enum import Enum


class CommunicationTypeChoice(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    BOTH = "both"



class MessageTemplate(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=256, null=True)
    communication_type = fields.CharEnumField(CommunicationTypeChoice, max_length=32, null=True)
    category = fields.CharField(max_length=32, null=True)
    status = fields.CharField(max_length=8, choices=[('active', 'Active'), ('draft', 'Draft')], default='draft')
    subject = fields.CharField(max_length=256, null = True)
    message = fields.TextField(null = True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class Message(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="messages", null=True)
    user = fields.ForeignKeyField("models.User", related_name="messages", null=True)
    template = fields.ForeignKeyField("models.MessageTemplate", related_name="messages", null=True)
    communication_type = fields.CharEnumField(CommunicationTypeChoice, max_length=32, null=True)
    subject = fields.CharField(max_length=256, null=True)
    message = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)