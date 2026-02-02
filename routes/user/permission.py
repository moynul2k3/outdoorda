from fastapi import APIRouter, HTTPException, status, Depends, Form
from applications.user.models import User, Permission, Group
from app.auth import permission_required
from tortoise.contrib.pydantic import pydantic_model_creator

router = APIRouter(tags=['Permission'])

# Pydantic schemas
Group_Pydantic = pydantic_model_creator(Group, name="Group", exclude=[])
Permission_Pydantic = pydantic_model_creator(Permission, name="Permission", exclude=[])


# -------------------------------
# Create Group -> superuser only
# -------------------------------
@router.post("/groups", response_model=dict, dependencies=[
    Depends(permission_required("add_group")),
])
async def create_group(
    name: str = Form(..., description="Group name"),
):
    if await Group.filter(name=name).exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group already exists")
    group = await Group.create(name=name)
    return {"message": f"Group '{group.name}' created", "id": group.id}


# -------------------------------
# List Groups -> include permissions -> staff + superuser
# -------------------------------
@router.get("/groups", response_model=list[dict], dependencies=[
    Depends(permission_required("view_group")),
])
async def list_groups():
    groups = await Group.all().prefetch_related("permissions")
    result = []
    for group in groups:
        result.append({
            "id": group.id,
            "name": group.name,
            "permissions": [perm.codename for perm in group.permissions]  # return permission codes
        })
    return result


# -----------------------------------------
# Assign permissions to group -> superuser only
# -----------------------------------------
@router.post("/groups/{group_id}/permissions", response_model=dict, dependencies=[
    Depends(permission_required("update_group")),
])
async def assign_permissions_to_group(
    group_id: int,
    permission_ids: list[int] = Form(..., description="List of permission IDs"),
):
    group = await Group.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    permissions = await Permission.filter(id__in=permission_ids)
    if not permissions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No valid permissions found")

    await group.permissions.add(*permissions)
    return {
        "message": f"Permissions assigned to group '{group.name}'",
        "permissions": [perm.codename for perm in permissions]
    }


# -------------------------------
# List all permissions
# -------------------------------
@router.get("/permissions", response_model=list[dict], dependencies=[
    Depends(permission_required("view_permission")),
])
async def list_permissions():
    permissions = await Permission.all()
    return [{"id": perm.id, "name": perm.name, "codename": perm.codename} for perm in permissions]
