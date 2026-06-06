from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


class ActivityLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    try:
        from .models import ActivityLog
        ActivityLog.log(
            user=user,
            action='user_login',
            description=f'{user.get_full_name() or user.username} logged in',
            request=request
        )
    except Exception:
        pass


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    try:
        from .models import ActivityLog
        if user:
            ActivityLog.log(
                user=user,
                action='user_logout',
                description=f'{user.get_full_name() or user.username} logged out',
                request=request
            )
    except Exception:
        pass