from core.models import UserProfile

def get_user_shop(user):
    """
    Safely returns the shop for a logged-in user
    """
    return UserProfile.objects.get(user=user).shop