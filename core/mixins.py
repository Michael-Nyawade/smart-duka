from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from core.utils import get_user_shop


class ShopRequiredMixin(LoginRequiredMixin):
    """
    Provides access to the current user's shop.

    Any view using this mixin gets a validated shop attribute.
    """

    shop = None

    def dispatch(self, request, *args, **kwargs):
        self.shop = get_user_shop(request.user)

        if self.shop is None:
            raise PermissionDenied(
                "User is not assigned to a shop."
            )

        return super().dispatch(request, *args, **kwargs)