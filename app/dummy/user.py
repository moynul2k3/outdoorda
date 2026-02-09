import random
from tortoise.transactions import in_transaction
from tortoise.exceptions import IntegrityError

from applications.user.models import User, UserRole

# ==================================================
# USERS (MATCHES User MODEL EXACTLY)
# ==================================================

# 1 Admin
USERS = [
    {
        "email": "admin@gmail.com",
        "name": "System Admin",
        "password": "admin",
        "role": UserRole.ADMIN,
        "is_staff": True,
        "is_active": True,
    }
]

roles = [UserRole.INSTALLER, UserRole.CUSTOMER]

for i in range(1, 50):
    role = random.choice(roles)

    if role == UserRole.INSTALLER:
        password = "installer"
        is_staff = True
    else:
        password = "customer"
        is_staff = False

    user_data = {
        "email": f"user{i}@example.com",
        "name": f"{role.value.title()} User {i}",
        "password": password,
        "role": role,
        "is_staff": is_staff,
        "is_active": True,
    }
    USERS.append(user_data)


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

            print("\n🎉 50 User seeding completed successfully!")

    except IntegrityError as e:
        print("❌ Integrity error:", e)
    except Exception as e:
        print("❌ Unexpected error:", e)
