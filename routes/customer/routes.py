from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Response, UploadFile, File, Query
from pydantic import BaseModel
from applications.user.models import User, UserRole
from applications.customer.pets import Pet
from applications.customer.models import InstallerReview
from app.token import get_current_user
from app.auth import login_required, role_required
from app.utils.file_manager import save_file
from typing import Optional
from datetime import datetime





router = APIRouter(tags=['Customer'])



#===============================================================
#                   Pet Endpoints
#===============================================================
@router.post("/pets/")
async def create_pet(
    name: str = Form(...),
    type: str = Form(...),
    size: str = Form(...),
    breed: Optional[str] = Form(None),
    user: User = Depends(role_required(UserRole.CUSTOMER))
    ):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    pet = await Pet.create(
        owner_id=user.id,
        name=name,
        type=type,
        size=size,
        breed=breed
    )

    return {"pet": pet}


@router.get("/pets/")
async def list_pets(
    user: User = Depends(get_current_user)
    ):
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    pets = await Pet.filter(owner_id=user.id).all()

    return {"pets": pets}


@router.get("/pets/{pet_id}")
async def get_pet(
    pet_id: str,
    user: User = Depends(get_current_user)
    ):
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    pet = await Pet.filter(id=pet_id, owner_id=user.id).first()
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")

    return {"pet": pet}

@router.delete("/pets/{pet_id}/")
async def delete_pet(
    pet_id: str,
    user: User = Depends(get_current_user)
    ):
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    pet = await Pet.filter(id=pet_id, owner_id=user.id).first()
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")
    
    await pet.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/pets/{pet_id}/")
async def update_pet(
    pet_id: str,
    name: Optional[str] = Form(None),
    type: Optional[str] = Form(None),
    size: Optional[str] = Form(None),
    breed: Optional[str] = Form(None),
    user: User = Depends(get_current_user)
    ):
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    pet = await Pet.filter(id=pet_id, owner_id=user.id).first()
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")
    
    if name is not None:
        pet.name = name
    if type is not None:
        pet.type = type
    if size is not None:
        pet.size = size
    if breed is not None:
        pet.breed = breed
    
    await pet.save()
    return {"pet": pet}



@router.post("/review")
async def review(
    installer_id: str = Form(...),
    rating: Optional[int] = Form(None),
    review: Optional[str] = Form(None),
    user: User = Depends(get_current_user)
    ):
    installer = await User.get(id=installer_id)
    if not installer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Installer not found")
    
    reviews = await InstallerReview.create(
        installer_id = installer_id,
        user_id = user.id,
        rating = rating,
        review = review
    )


    return {"review": reviews}
