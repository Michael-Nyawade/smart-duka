from core.models import UserProfile

def get_user_shop(user):
    return getattr(user.userprofile, "shop", None)


def for_current_shop(queryset, user):
    """
    Filters a queryset to only include objects belonging to the current user's shop
    """
    shop = get_user_shop(user)
    return queryset.filter(shop=shop)
