from sales.models import AuditLog


def log_action(*, user, action):
    """
    Central audit logging helper.
    Keeps logging consistent across app.
    """

    AuditLog.objects.create(
        user=user,
        action=action
    )