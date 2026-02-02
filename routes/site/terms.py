from fastapi import APIRouter, HTTPException, Depends
from applications.site.models import Terms  # Adjust import according to your project
from tortoise.contrib.pydantic import pydantic_model_creator
from app.auth import role_required
from applications.user.models import UserRole

router = APIRouter(prefix="/terms", tags=["Terms Info"])

Terms_Pydantic = pydantic_model_creator(Terms, name="Terms")
TermsIn_Pydantic = pydantic_model_creator(Terms, name="TermsIn", exclude_readonly=True)

# -----------------------------
# Get the terms entry
# -----------------------------
@router.get("/", response_model=Terms_Pydantic)
async def get_terms():
    terms = await Terms.first()  # Get the first (or only) entry
    if not terms:
        raise HTTPException(status_code=404, detail="Terms entry not found")
    return await Terms_Pydantic.from_tortoise_orm(terms)


# -----------------------------
# Create or update terms
# -----------------------------
@router.post("/", response_model=Terms_Pydantic, dependencies=[Depends(role_required(UserRole('ADMIN')))])
async def create_or_update_terms(payload: TermsIn_Pydantic):
    terms = await Terms.first()

    if terms:
        # Update existing entry
        await terms.update_from_dict(payload.dict(exclude_unset=True))
        await terms.save()
    else:
        # Create new entry
        terms = await Terms.create(**payload.dict(exclude_unset=True))

    return await Terms_Pydantic.from_tortoise_orm(terms)
