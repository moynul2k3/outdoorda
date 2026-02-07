from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Response, UploadFile, File, Query
from pydantic import BaseModel
from applications.user.models import User, UserRole
from app.token import get_current_user
from applications.customer.posts import PostRequest, Bid, InstallationSurface, StatusEnum
from app.auth import login_required, role_required
from app.utils.file_manager import save_file
from typing import Optional
from datetime import datetime





router = APIRouter(tags=['Customer Posts'])




@router.post("/posts/")
async def create_post(
    pet_name: str = Form(...),
    pet_type: str = Form(...),
    price: float = Form(...),
    size: str = Form(...),
    installation_surface: InstallationSurface = Form(...),
    address: str = Form(...),
    photos: list[UploadFile] = File(None),
    user: User = Depends(role_required(UserRole.CUSTOMER))
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    photo_urls = []
    if photos:
        for photo in photos:
            if photo.filename:
                file_url = await save_file(photo, upload_to="post_photos")
                photo_urls.append(file_url)



    post = await PostRequest.create(
        customer_id=user.id,
        pet_name=pet_name,
        pet_type=pet_type,
        price=price,
        size=size,
        installation_surface=installation_surface,
        Address=address,
        photos=photo_urls
    )

    return {"post": post}



@router.get("/posts/")
async def list_posts(
    status: StatusEnum | None = Query(None),
    user: User = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    filters = {"customer_id": user.id}
    if status:
        filters["status"] = status

    posts = await PostRequest.filter(**filters).order_by("-created_at")
    return {"posts": posts}


@router.get("/posts/{post_id}/")
async def get_post(
    post_id: str,
    user: User = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    post = await PostRequest.filter(id=post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return {"post": post}


@router.post("/posts/{post_id}/bids/")
async def place_bid(
    post_id: str,
    price: float = Form(...),
    note: str = Form(None),
    user: User = Depends(role_required(UserRole.INSTALLER))
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    post = await PostRequest.filter(id=post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.status not in [StatusEnum.RECEIVING_BIDS, StatusEnum.PENDING]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bids are not being accepted for this post")

    bid = await Bid.create(
        post_request_id=post.id,
        installer_id=user.id,
        price=price,
        note=note
    )
    post.status = StatusEnum.RECEIVING_BIDS
    await post.save()

    return {"bid": bid}



@router.get("/posts-bids/")
async def list_bids(
    post_id: Optional[str] = Query(None),
    user: User = Depends(get_current_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    print("USER ROLE:", user.role)
    
    if post_id and user.role == UserRole.CUSTOMER:
        print("hello")
        post = await PostRequest.filter(id=post_id, customer_id=user.id).first()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        bids = await Bid.filter(post_request_id=post.id).order_by("-created_at")
    elif post_id and user.role == UserRole.INSTALLER:
        print("INSTALLER BID LISTING FOR POST:", post_id, "USER ID:", user.id)
        post = await PostRequest.filter(id=post_id).first()
        print("FOUND POST:", post)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        bids = await Bid.filter(post_request_id=post.id, installer_id=user.id).order_by("-created_at")
    elif not post_id and user.role == UserRole.INSTALLER:
        print("INSTALLER ALL BIDS LISTING FOR USER ID:", user.id)
        bids = await Bid.filter(installer_id=user.id).order_by("-created_at")
        print("INSTALLER ALL BIDS:", bids)
        return {"bids": bids}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    return {"post": post, "bids": bids}




@router.post("/bid/{bid_id}/accept/")
async def accept_bid(
    bid_id: str,
    user: User = Depends(role_required(UserRole.CUSTOMER))
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    bid = await Bid.filter(id=bid_id).first()
    if not bid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bid not found")

    post = await PostRequest.filter(id=bid.post_request_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.customer_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    
    post.installer_id = bid.installer_id
    post.status = StatusEnum.INSTALLER_ASSIGNED
    post.price = bid.price
    post.assigned_at = datetime.now()

    await post.save()

    return {"message": "Bid accepted successfully", "post": post}




@router.post("/post/{post_id}/accept/")
async def accept_post_without_bid(
    post_id: str,
    user: User = Depends(role_required(UserRole.INSTALLER))
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    post = await PostRequest.filter(id=post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.status not in [StatusEnum.PENDING, StatusEnum.RECEIVING_BIDS]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post cannot be accepted at this stage")

    post.installer_id = user.id
    post.status = StatusEnum.INSTALLER_ASSIGNED
    post.assigned_at = datetime.now()

    await post.save()

    return {"message": "Post accepted without bid successfully", "post": post}




@router.patch("/posts/{post_id}/update/")
async def update_post(
    post_id: str,
    status: Optional[StatusEnum] = Form(None),
    scheduled_date: Optional[datetime] = Form(None),
    note: Optional[str] = Form(None),
    is_additional_service: Optional[bool] = Form(None),
    additional_service_note: Optional[str] = Form(None),
    is_customer_satisfied: Optional[bool] = Form(None),
    customer_satisfaction_note: Optional[str] = Form(None),
    user: User = Depends(get_current_user)
):
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        
        post = await PostRequest.filter(id=post_id).first()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        update_fields = {}
        if status is not None:
            update_fields["status"] = status
        if scheduled_date is not None:
            update_fields["scheduled_date"] = scheduled_date
        if note is not None:
            update_fields["note"] = note
        if is_additional_service is not None:
            update_fields["is_additional_service"] = is_additional_service
        if additional_service_note is not None:
            update_fields["additional_service_note"] = additional_service_note
        if is_customer_satisfied is not None:
            update_fields["is_customer_satisfied"] = is_customer_satisfied
        if customer_satisfaction_note is not None:
            update_fields["customer_satisfaction_note"] = customer_satisfaction_note

        for field, value in update_fields.items():
            setattr(post, field, value)

        await post.save()

        return {"message": "Post updated successfully", "post": post}