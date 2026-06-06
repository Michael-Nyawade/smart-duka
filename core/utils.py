from core.models import UserProfile

def get_user_shop(user):
    """
    Safely returns the shop for a logged-in user
    """
    return UserProfile.objects.get(user=user).shop

def for_current_shop(queryset, user):
    """
    Filters a queryset to only include objects belonging to the current user's shop
    """
    shop = get_user_shop(user)
    return queryset.filter(shop=shop)
