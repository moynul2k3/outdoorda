from tortoise.transactions import in_transaction
from tortoise.exceptions import IntegrityError

from applications.user.models import User, UserRole

# ==================================================
# USERS (MATCHES User MODEL EXACTLY)
# ==================================================

USERS = [
    {
        "email": "admin@gmail.com",
        "name": "System Admin",
        "password": "admin123",
        "role": UserRole.ADMIN,
        "is_staff": True,
        "is_active": True,
    },
    {
        "email": "installer@gmail.com",
        "name": "Main Installer",
        "password": "installer123",
        "role": UserRole.INSTALLER,
        "is_staff": True,
        "is_active": True,
    },
    {
        "email": "customer1@gmail.com",
        "name": "Customer One",
        "password": "customer123",
        "role": UserRole.CUSTOMER,
        "is_staff": False,
        "is_active": True,
    },
    {
        "email": "customer2@gmail.com",
        "name": "Customer Two",
        "password": "customer123",
        "role": UserRole.CUSTOMER,
        "is_staff": False,
        "is_active": True,
    },
]

# ==================================================
# MAIN SEED FUNCTION
# ==================================================

async def seed_users():
    try:
        async with in_transaction():

            for user_data in USERS:
                raw_password = user_data.pop("password")

                user = await User.get_or_none(email=user_data["email"])

                if not user:
                    user = User(**user_data)
                    user.password = raw_password  # hashed in save()
                    await user.save()
                    print(f"✅ Created user: {user.email}")
                else:
                    print(f"⚠️ User already exists: {user.email}")

            print("\n🎉 User seeding completed successfully!")

    except IntegrityError as e:
        print("❌ Integrity error:", e)
    except Exception as e:
        print("❌ Unexpected error:", e)
