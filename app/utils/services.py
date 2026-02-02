from typing import Type
from tortoise.models import Model

async def get_all(model: Type[Model]):
    return await model.all()

async def get_one(model: Type[Model], obj_id: int):
    return await model.get_or_none(id=obj_id)

async def create_instance(model: Type[Model], data: dict):
    instance = await model.create(**data)
    return instance

async def update_instance(model: Type[Model], obj_id: int, data: dict):
    instance = await model.get_or_none(id=obj_id)
    if not instance:
        return None
    for key, value in data.items():
        setattr(instance, key, value)
    await instance.save()
    return instance

async def delete_instance(model: Type[Model], obj_id: int):
    instance = await model.get_or_none(id=obj_id)
    if instance:
        await instance.delete()
        return True
    return False
