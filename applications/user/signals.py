from tortoise.signals import post_save
from applications.user.models import User

# async def create_user_profile(sender, instance: User, created: bool, **kwargs):
#     if created:
#         profile = Profile(user=instance)
#         await profile.save()
#         print(f"✅ Profile created for user: {instance.username}")
#
# post_save(User)(create_user_profile)