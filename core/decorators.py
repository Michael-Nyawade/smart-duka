from django.http import HttpResponseForbidden
from functools import wraps
from core.utils import get_user_role


def allowed_roles(roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            role = get_user_role(request.user)

            if role in roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden(
                "You do not have permission to access this page."
            )

        return wrapper

    return decorator