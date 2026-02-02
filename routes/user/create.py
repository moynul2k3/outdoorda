from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Form, UploadFile, File
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.transactions import in_transaction

from app.auth import role_required
from applications.user.models import User, UserRole
from app.utils.file_manager import save_file

router = APIRouter(prefix="/users/create", tags=["Create Users"])

# Serializers
UserOut = pydantic_model_creator(User, name="UserOut", exclude=("password",))


async def serialize_user(user: User) -> Dict[str, Any]:
    await user.fetch_related(
        "groups",
        "user_permissions",
    )

    groups = await user.groups.all()
    permissions = await user.user_permissions.all()

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,

        "photo": user.photo,
        "phone": user.phone,

        "role": user.role,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "groups": [{"id": g.id, "name": g.name} for g in groups],
        "permissions": [{"id": p.id, "codename": p.codename, "name": p.name} for p in permissions],
    }

@router.post("/create", response_model=Dict[str, Any], dependencies=[Depends(role_required(UserRole('ADMIN')))], description="Only ADMIN can create users")
async def create_user(
    email: str = Form(...),
    password: str = Form(...),
    name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    role: Optional[UserRole] = Form(UserRole.CUSTOMER),
    is_active: Optional[bool] = Form(True),
    photo: Optional[UploadFile] = File(None),
):
    # Check if user already exists
    existing = await User.get_or_none(email=email)
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Save photo if provided
    photo_path = None
    if photo:
        photo_path = await save_file(photo, upload_to="users")

    async with in_transaction():
        user = await User.create(
            email=email,
            password=password,
            name=name,
            phone=phone,
            role=role,
            photo=photo_path,
            is_active=is_active
        )

    return await serialize_user(user)
