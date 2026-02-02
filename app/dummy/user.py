from tortoise.transactions import in_transaction
from tortoise.exceptions import IntegrityError

from applications.user.models import (
    User,
    Group,
    Permission,
    UserRole,
)

# ==================================================
# PERMISSIONS
# ==================================================

PERMISSIONS = [
    ("View Patients", "view_patient"),
    ("Edit Patients", "update_patient"),
    ("Create Recall", "add_recall"),
    ("Assign Recall", "assign_recall"),
    ("Send Message", "send_message"),
    ("View Reports", "view_reports"),
]

# ==================================================
# GROUPS → PERMISSIONS
# ==================================================

GROUPS = {
    "Agents": [
        "view_patient",
        "send_message",
    ],
    "Managers": [
        "view_patient",
        "add_recall",
        "assign_recall",
        "view_reports",
    ],
    "Admins": [
        "view_patient",
        "update_patient",
        "add_recall",
        "assign_recall",
        "send_message",
        "view_reports",
    ],
}

# ==================================================
# USERS
# ==================================================

USERS = [
    {
        "email": "admin@gmail.com",
        "name": "Admin User",
        "password": "admin",
        "role": UserRole.ADMIN,
        "is_staff": True,
        "is_superuser": True,
        "groups": ["Admins"],
    },
    {
        "email": "manager@gmail.com",
        "name": "Manager User",
        "password": "manager",
        "role": UserRole.MANAGER,
        "is_staff": True,
        "groups": ["Managers"],
    },
    {
        "email": "agent1@gmail.com",
        "name": "Agent One",
        "password": "agent",
        "role": UserRole.AGENT,
        "groups": ["Agents"],
    },
    {
        "email": "agent2@gmail.com",
        "name": "Agent Two",
        "password": "agent",
        "role": UserRole.AGENT,
        "groups": ["Agents"],
    },
]

# ==================================================
# MAIN SEED FUNCTION
# ==================================================
async def seed_auth_data():
    try:
        async with in_transaction():
            # -----------------------------
            # Permissions
            # -----------------------------
            permission_map = {}
            for name, codename in PERMISSIONS:
                perm, _ = await Permission.get_or_create(
                    codename=codename,
                    defaults={"name": name},
                )
                permission_map[codename] = perm

            print("✅ Permissions ensured")

            # -----------------------------
            # Groups
            # -----------------------------
            group_map = {}
            for group_name, perm_codes in GROUPS.items():
                group, _ = await Group.get_or_create(name=group_name)
                perms = [permission_map[c] for c in perm_codes]
                await group.permissions.add(*perms)
                group_map[group_name] = group

            print("✅ Groups & permissions ensured")

            # -----------------------------
            # Users
            # -----------------------------
            for user_data in USERS:
                groups = user_data.pop("groups", [])
                password = user_data.pop("password")

                # Remove keys that are not fields on User
                user_data.pop("is_superuser", None)

                # Try to get user by email
                user = await User.get_or_none(email=user_data["email"])
                if not user:
                    # Create user
                    user = User(**user_data)
                    user.password = User.set_password(password)
                    await user.save()
                    print(f"✅ Created user: {user.email}")
                else:
                    print(f"⚠️ User exists: {user.email}")

                # Assign groups
                for group_name in groups:
                    await user.groups.add(group_map[group_name])

            print("\n🎉 Auth seeding completed successfully!")

    except IntegrityError as e:
        print("❌ Integrity error:", e)
    except Exception as e:
        print("❌ Unexpected error:", e)
