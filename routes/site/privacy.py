from fastapi import APIRouter, HTTPException, Depends

from app.auth import role_required
from applications.site.models import Privacy  # Adjust import according to your project
from tortoise.contrib.pydantic import pydantic_model_creator

from applications.user.models import UserRole

router = APIRouter(prefix="/privacy", tags=["Privacy Info"])

Privacy_Pydantic = pydantic_model_creator(Privacy, name="Privacy")
PrivacyIn_Pydantic = pydantic_model_creator(Privacy, name="PrivacyIn", exclude_readonly=True)

@router.get("/", response_model=Privacy_Pydantic)
async def get_privacy():
    privacy = await Privacy.first()  # Get the first (or only) entry
    if not privacy:
        raise HTTPException(status_code=404, detail="Privacy entry not found")
    return await Privacy_Pydantic.from_tortoise_orm(privacy)


# -----------------------------
# Create or update privacy
# -----------------------------
@router.post("/", response_model=Privacy_Pydantic, dependencies=[Depends(role_required(UserRole('ADMIN')))])
async def create_or_update_privacy(payload: PrivacyIn_Pydantic):
    privacy = await Privacy.first()

    if privacy:
        # Update existing entry
        await privacy.update_from_dict(payload.dict(exclude_unset=True))
        await privacy.save()
    else:
        # Create new entry
        privacy = await Privacy.create(**payload.dict(exclude_unset=True))

    return await Privacy_Pydantic.from_tortoise_orm(privacy)
