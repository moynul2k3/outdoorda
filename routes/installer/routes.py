from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Response, UploadFile, File, Query
from pydantic import BaseModel
from tortoise.functions import Sum
from applications.user.models import User, UserRole
from app.token import get_current_user
from applications.customer.posts import PostRequest, Bid, InstallationSurface, StatusEnum
from app.auth import login_required, role_required
from app.utils.file_manager import save_file
from typing import Optional
from datetime import datetime





router = APIRouter(tags=['Installer'])




#===============================================================
#                   Installer this month earnings Endpoint
#===============================================================



@router.get("/installer/earnings/")
async def get_installer_earnings(
    user: User = Depends(role_required(UserRole.INSTALLER))
    ):
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    
    today = datetime.now()
    start_of_month = datetime(today.year, today.month, 1)
    query = PostRequest.filter(
        installer_id = user.id,
        assigned_at__gte=start_of_month,
        assigned_at__lt=today
    )

    in_progress_count = await query.filter(status=StatusEnum.IN_PROGRESS).count()
    completed_count = await query.filter(status=StatusEnum.COMPLETED).count()

    result = await query.filter(
            status=StatusEnum.COMPLETED
        ).annotate(
            total=Sum("price")
        ).values("total")
    
    earnings = result[0]["total"] if result and result[0]["total"] else 0.0


    return {"installer_id": user.id, "in_progress_count": in_progress_count, "completed_count": completed_count, "earnings": earnings}