from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Response, UploadFile, File, Query
from pydantic import BaseModel
from applications.user.models import User, UserRole
from app.config import settings
from app.token import get_current_user
from applications.customer.posts import PostRequest, Bid, InstallationSurface, StatusEnum
from applications.payments.models import Payment, Payout
from app.auth import login_required, role_required
from app.utils.file_manager import save_file
from typing import Optional
from datetime import datetime
import stripe




router = APIRouter(tags=['Payments'])



stripe.api_key = settings.STRIPE_SECRET_KEY



@router.post("/installer/stripe/create-account")
async def create_installer_stripe_account(
    user: User = Depends(role_required(UserRole.INSTALLER))
):
    if user.stripe_account_id:
        return {"account_id": user.stripe_account_id}

    account = stripe.Account.create(
        type="express",
        country="US",
        email=user.email,
        capabilities={
            "card_payments": {"requested": True},
            "transfers": {"requested": True},
        },
    )

    user.stripe_account_id = account.id
    await user.save()

    return {"account_id": account.id}




@router.post("/installer/stripe/onboarding-link")
async def get_onboarding_link(
    user: User = Depends(role_required(UserRole.INSTALLER))
):
    if not user.stripe_account_id:
        raise HTTPException(400, "Stripe account not created")

    link = stripe.AccountLink.create(
        account=user.stripe_account_id,
        refresh_url="https://127.0.0.1:8000/stripe/refresh",
        return_url="https://127.0.0.1:8000/stripe/success",
        type="account_onboarding",
    )

    return {"url": link.url}


@router.get("/account-is-ready")
async def account_ready(
    user: User = Depends(role_required(UserRole.INSTALLER))
    ):

    account = stripe.Account.retrieve(user.stripe_account_id)

    if not account.charges_enabled:
        raise HTTPException(400, "Installer not ready for payments")
    

    return account





@router.post("/payments/create")
async def create_payment_intent(
    post_id: str,
    user: User = Depends(role_required(UserRole.CUSTOMER))
):
    post = await PostRequest.get(id=post_id).prefetch_related("installer")

    if post.status not in [StatusEnum.IN_PROGRESS, StatusEnum.INSTALLER_ASSIGNED]:
        raise HTTPException(400, "Job not in stage of payment")

    installer = post.installer

    if not installer.stripe_account_id:
        raise HTTPException(400, "Installer not connected to Stripe")

    amount = int(post.price * 100)  # cents
    platform_fee = int(amount * 0.10)  # 10% fee

    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",
        automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
       

        transfer_data={
            "destination": installer.stripe_account_id
        },

        application_fee_amount=platform_fee,

        metadata={
            "post_id": str(post.id),
            "installer_id": installer.id,
            "customer_id": user.id,
        }
    )


    payment = await Payment.create(
    post=post,
    customer=user,
    installer=installer,
    stripe_payment_intent_id=intent.id,
    amount=amount,
    platform_fee=platform_fee,
    installer_amount=amount - platform_fee,
    currency="usd",
    status="pending"
)

    return {
        "client_secret": intent.client_secret,
        "payment": payment
    }




@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        post_id = intent["metadata"]["post_id"]

        post = await PostRequest.get(id=post_id)
        post.status = StatusEnum.COMPLETED
        await post.save()

        payment = await Payment.get(post_id = post.id)
        payment.status = "succeeded"
        await payment.save()

    return {"status": "success"}
